from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.repository import add_audit, add_document, find_document_by_hash, get_application, get_document, list_documents, new_id
from app.db.session import get_db
from app.schemas.document import DocumentRecord, DocumentType
from app.services.storage_service import save_document, sha256_bytes, validate_upload
from app.api.dependencies import bind_application_id

router = APIRouter(
    prefix="/applications/{application_id}/documents",
    tags=["documents"],
    dependencies=[Depends(bind_application_id)],
)


def _record(row) -> DocumentRecord:
    return DocumentRecord(document_id=row.id, application_id=row.application_id, file_name=row.file_name,
        storage_uri=row.storage_uri, file_hash=row.file_hash, media_type=row.media_type, file_size_bytes=row.file_size_bytes,
        document_type=row.document_type, status=row.status, created_at=row.created_at)


@router.post('', response_model=DocumentRecord, status_code=201)
async def upload_document(application_id: str, file: UploadFile = File(...),
                          document_type: DocumentType = Form(DocumentType.UNKNOWN), db: Session = Depends(get_db)):
    if not get_application(db, application_id):
        raise HTTPException(status_code=404, detail='Application not found')
    data = await file.read()
    try:
        validate_upload(file.filename or 'document', data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    digest = sha256_bytes(data)
    duplicate = find_document_by_hash(db, application_id, digest)
    if duplicate:
        add_audit(db, application_id, 'DUPLICATE_DOCUMENT_REJECTED', document_id=duplicate.id, actor='api', metadata={'file_name': file.filename})
        raise HTTPException(status_code=409, detail=f'Duplicate document already uploaded as {duplicate.id}')
    document_id = new_id('DOC')
    path = save_document(application_id, document_id, file.filename or 'document', data)
    row = add_document(db, id=document_id, application_id=application_id, file_name=file.filename or Path(path).name,
        storage_uri=str(path), file_hash=digest, media_type=file.content_type, file_size_bytes=len(data),
        document_type=document_type.value, status='UPLOADED')
    add_audit(db, application_id, 'DOCUMENT_UPLOADED', document_id=row.id, actor='api', metadata={'file_name': row.file_name, 'size': len(data)})
    return _record(row)


@router.get('', response_model=list[DocumentRecord])
def list_documents_endpoint(application_id: str, db: Session = Depends(get_db)):
    if not get_application(db, application_id):
        raise HTTPException(status_code=404, detail='Application not found')
    return [_record(row) for row in list_documents(db, application_id)]


@router.get('/{document_id}', response_model=DocumentRecord)
def get_document_endpoint(application_id: str, document_id: str, db: Session = Depends(get_db)):
    row = get_document(db, document_id)
    if not row or row.application_id != application_id:
        raise HTTPException(status_code=404, detail='Document not found')
    return _record(row)
