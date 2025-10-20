from datetime import datetime
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from api.config import settings, get_db
from api import models, schemas
from api.database import init_db
from api.services.obrasgov_client import ObrasGovClient
from api.services.data_processor import DataProcessor

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    try:
        from api.config import SessionLocal
        db = SessionLocal()
        try:
            await sync_projects(uf="DF", db=db)
            print("Sync inicial executado com sucesso!")
        except Exception as e:
            print(f"Erro no sync inicial: {str(e)}")
        finally:
            db.close()
    except Exception as e:
        print(f"Erro na configuração do sync inicial: {str(e)}")

    scheduler.add_job(
        scheduled_sync,
        'cron',
        hour=settings.SYNC_SCHEDULE_HOUR,
        minute=settings.SYNC_SCHEDULE_MINUTE
    )
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(
    title="ObrasGov API - Distrito Federal",
    description="API para extração e armazenamento de dados de projetos de investimento do DF",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", tags=["Health"])
async def root():
    return {"message": "ObrasGov API - use /docs para documentação"}


@app.get("/health", response_model=schemas.HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return schemas.HealthResponse(
        status="ok",
        database=db_status,
        timestamp=datetime.utcnow()
    )


@app.get("/ready", tags=["Health"])
async def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        projeto_count = db.query(models.ProjetoInvestimento).count()

        if projeto_count == 0:
            raise HTTPException(
                status_code=503,
                detail="Database not populated yet. Initial sync still running."
            )

        return {
            "status": "ready",
            "database": "connected",
            "projects_count": projeto_count,
            "timestamp": datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service not ready: {str(e)}"
        )


@app.post("/sync", response_model=schemas.SyncResponse, tags=["Sincronização"])
async def sync_projects(uf: str = "DF", db: Session = Depends(get_db)):
    start_time = datetime.utcnow()

    try:
        client = ObrasGovClient()
        processor = DataProcessor(db)
        total_projetos = 0

        async for page_response in client.fetch_all(uf):
            for projeto_data in page_response.content:
                try:
                    processor.process_projeto(projeto_data)
                    total_projetos += 1
                except Exception as e:
                    continue

            db.commit()

        total_executores = db.query(models.Executor).count()
        total_tomadores = db.query(models.Tomador).count()
        total_repassadores = db.query(models.Repassador).count()

        return schemas.SyncResponse(
            message=f"Sincronização concluída com sucesso para {uf}",
            total_projetos=total_projetos,
            total_executores=total_executores,
            total_tomadores=total_tomadores,
            total_repassadores=total_repassadores,
            sync_time=str(datetime.utcnow() - start_time)
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro na sincronização: {str(e)}")


@app.get("/projetos", response_model=List[schemas.ProjetoResponse], tags=["Projetos"])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    uf: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.ProjetoInvestimento)

    if uf:
        query = query.filter(models.ProjetoInvestimento.uf == uf)

    projetos = query.offset(skip).limit(limit).all()
    return projetos


@app.get("/projetos/{id_unico}", response_model=schemas.ProjetoResponse, tags=["Projetos"])
async def get_project(id_unico: str, db: Session = Depends(get_db)):
    projeto = db.query(models.ProjetoInvestimento).filter(
        models.ProjetoInvestimento.id_unico == id_unico
    ).first()

    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    return projeto


async def scheduled_sync():
    from api.config import SessionLocal
    db = SessionLocal()
    try:
        await sync_projects(uf="DF", db=db)
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
