from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from langflow.services.database.models.task.model import Task, TaskCreate, TaskRead, TaskUpdate
from langflow.services.deps import get_session, get_task_orchestration_service
from langflow.services.task_orchestration.service import TaskOrchestrationService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskRead)
async def create_task(
    task_create: TaskCreate,
    session: Session = Depends(get_session),
    task_orchestration_service: TaskOrchestrationService = Depends(get_task_orchestration_service),
):
    try:
        new_task = Task.model_validate(task_create)
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        # Attempt to orchestrate the task, but continue if it fails
        try:
            task_orchestration_service.orchestrate_task(new_task)
        except Exception:
            pass

        return new_task
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[TaskRead])
async def read_tasks(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    tasks = session.exec(select(Task).offset(skip).limit(limit)).all()
    return tasks


@router.get("/{task_id}", response_model=TaskRead)
async def read_task(
    task_id: UUID,
    session: Session = Depends(get_session),
):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    session: Session = Depends(get_session),
    task_orchestration_service: TaskOrchestrationService = Depends(get_task_orchestration_service),
):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task_update.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)

    # Attempt to re-orchestrate the task after update, but continue if it fails
    try:
        task_orchestration_service.orchestrate_task(task)
    except Exception:
        pass

    return task


@router.delete("/{task_id}", response_model=TaskRead)
async def delete_task(
    task_id: UUID,
    session: Session = Depends(get_session),
):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return task
