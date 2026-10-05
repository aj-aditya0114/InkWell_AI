"""Reducer subgraph nodes.

Flow:
    merge_content -> decide_images -> generate_and_place_images
"""

from pathlib import Path

from langchain_core.messages import SystemMessage, HumanMessage

from ..config import llm
from ..schemas import GlobalImagePlan
from ..state import State
from .image_generation import gemini_generate_image_bytes, safe_slug


def merge_content(state: State) -> dict:
    """Merge parallel worker sections into the original task order."""
    plan = state["plan"]

    if plan is None:
        raise ValueError("merge_content called without plan.")

    ordered_sections = [
        md for _, md in sorted(state["sections"], key=lambda x: x[0])
    ]

    body = "\n\n".join(ordered_sections).strip()
    merged_md = f"# {plan.blog_title}\n\n{body}\n"

    return {"merged_md": merged_md}


DECIDE_IMAGES_SYSTEM = """You are an expert technical editor.
Decide if images/diagrams are needed for THIS blog.

Rules:
- Max 3 images total.
- Each image must materially improve understanding (diagram/flow/table-like visual).
- Insert placeholders exactly: [[IMAGE_1]], [[IMAGE_2]], [[IMAGE_3]].
- If no images needed: md_with_placeholders must equal input and images=[].
- Avoid decorative images; prefer technical diagrams with short labels.
Return strictly GlobalImagePlan.
"""


def decide_images(state: State) -> dict:
    """Analyze the merged article and create an optional image plan."""
    planner = llm.with_structured_output(GlobalImagePlan)
    merged_md = state["merged_md"]
    plan = state["plan"]

    assert plan is not None

    image_plan = planner.invoke(
        [
            SystemMessage(content=DECIDE_IMAGES_SYSTEM),
            HumanMessage(
                content=(
                    f"Blog kind: {plan.blog_kind}\n"
                    f"Topic: {state['topic']}\n\n"
                    "Insert placeholders + propose image prompts.\n\n"
                    f"{merged_md}"
                )
            ),
        ]
    )

    return {
        "md_with_placeholders": image_plan.md_with_placeholders,
        "image_specs": [
            img.model_dump()
            for img in image_plan.images
        ],
    }


def generate_and_place_images(state: State) -> dict:
    """Generate requested images, replace placeholders, and save markdown."""
    plan = state["plan"]
    assert plan is not None

    md = state.get("md_with_placeholders") or state["merged_md"]
    image_specs = state.get("image_specs", []) or []

    # If no images were requested, just write the markdown.
    if not image_specs:
        filename = f"{safe_slug(plan.blog_title)}.md"
        Path(filename).write_text(md, encoding="utf-8")
        return {"final": md}

    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)

    for spec in image_specs:
        placeholder = spec["placeholder"]
        filename = spec["filename"]
        out_path = images_dir / filename

        # Generate only if the image does not already exist.
        if not out_path.exists():
            try:
                img_bytes = gemini_generate_image_bytes(spec["prompt"])
                out_path.write_bytes(img_bytes)
            except Exception as e:
                # Graceful fallback: keep the document usable.
                prompt_block = (
                    f"> **[IMAGE GENERATION FAILED]** "
                    f"{spec.get('caption', '')}\n>\n"
                    f"> **Alt:** {spec.get('alt', '')}\n>\n"
                    f"> **Prompt:** {spec.get('prompt', '')}\n>\n"
                    f"> **Error:** {e}\n"
                )
                md = md.replace(placeholder, prompt_block)
                continue

        img_md = (
            f"![{spec['alt']}](images/{filename})\n"
            f"*{spec['caption']}*"
        )
        md = md.replace(placeholder, img_md)

    filename = f"{safe_slug(plan.blog_title)}.md"
    Path(filename).write_text(md, encoding="utf-8")

    return {"final": md}
