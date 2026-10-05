## By following these steps you can understand the backend code completely
1. config.py
      ↓
2. schemas.py
      ↓
3. state.py
      ↓
4. nodes/router.py
      ↓
5. nodes/research.py
      ↓
6. nodes/orchestrator.py
      ↓
7. nodes/worker.py
      ↓
8. reducer/nodes.py
      ↓
9. reducer/image_generation.py
      ↓
10. reducer/graph.py
      ↓
11. graph.py
      ↓
12. main.py



## Conceptual Flow
User Topic
    ↓
Router
    ↓
Need Research?
   / \
 No   Yes
 |     |
 |   Research
 |     |
 └──┬──┘
    ↓
Orchestrator
    ↓
Create Blog Plan
    ↓
Fan-out
    ↓
Workers
    ↓
Write Sections
    ↓
Reducer
    ↓
Merge Sections
    ↓
Decide Images
    ↓
Generate Images
    ↓
Final Markdown