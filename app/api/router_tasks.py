from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.database.db import Task, get_db
from app.api.models.task_models import TaskRead, TaskCreate, TaskUpdate

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    task = Task(title=payload.title, description=payload.description)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks", response_model=List[TaskRead])
def list_tasks(db: Session = Depends(get_db)) -> List[Task]:
    return db.query(Task).order_by(Task.id.asc()).all()


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return task


@router.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.is_done is not None:
        task.is_done = payload.is_done

    db.add(task)
    db.commit()
    db.refresh(task)
    return task
    

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task)
    db.commit()