from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .schemas import AnalyzeResponseSchema, ErrorResponseSchema, HistoryListResponseSchema
from .service import ResumeAnalysisService


def create_app(service: ResumeAnalysisService | None = None) -> FastAPI:
    service = service or ResumeAnalysisService()

    app = FastAPI(
        title="Resume Analyser API",
        version="4.0.0",
        description="FastAPI wrapper around the shared resume analysis core used by the desktop app.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", include_in_schema=False)
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/analyze",
        response_model=AnalyzeResponseSchema,
        status_code=201,
        summary="Upload and analyze a resume",
        responses={400: {"model": ErrorResponseSchema}},
    )
    async def analyze_resume_upload(
        resume: UploadFile = File(..., description="Resume file to analyze. PDF, DOCX, and TXT are supported by the shared parser."),
        job_description: str = Form(..., description="Job description or target role text to compare against."),
        similarity_mode: str = Form("tfidf", description="Primary scoring mode to use. Accepted values: tfidf or semantic."),
    ) -> AnalyzeResponseSchema:
        try:
            content = await resume.read()
            report = service.analyze_upload(
                resume_filename=resume.filename or "resume.txt",
                resume_content=content,
                job_description=job_description,
                similarity_mode=similarity_mode,
            )
        except Exception as exc:  # pragma: no cover - defensive wrapper for upload parsing and analysis failures
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return AnalyzeResponseSchema(report=report)

    @app.get(
        "/reports/{report_id}",
        response_model=AnalyzeResponseSchema,
        summary="Fetch a saved report by id",
        responses={404: {"model": ErrorResponseSchema}},
    )
    def get_report(report_id: str) -> AnalyzeResponseSchema:
        report = service.get_report(report_id)
        if report is None:
            raise HTTPException(status_code=404, detail="Report not found")

        return AnalyzeResponseSchema(report=report)

    @app.get(
        "/history",
        response_model=HistoryListResponseSchema,
        summary="List saved analysis history",
    )
    def list_history() -> HistoryListResponseSchema:
        return HistoryListResponseSchema(reports=service.list_history())

    return app


app = create_app()