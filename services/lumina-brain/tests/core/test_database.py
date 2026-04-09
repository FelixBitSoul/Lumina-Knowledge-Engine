import pytest
from sqlalchemy.orm import Session
from lumina_brain.core.services.database import get_db, init_db
from lumina_brain.core.models import Document, DocumentMetadata, DocumentProcessing, DocumentStatus, SourceType


@pytest.fixture(scope="module")
def db():
    # 初始化数据库
    init_db()
    # 获取数据库会话
    db = next(get_db())
    yield db
    # 清理数据库
    db.query(DocumentProcessing).delete()
    db.query(DocumentMetadata).delete()
    db.query(Document).delete()
    db.commit()
    db.close()


def test_document_creation(db: Session):
    """测试文档创建"""
    # 创建文档
    document = Document(
        id="test-doc-1",
        file_name="test.pdf",
        category="test",
        collection="knowledge_base",
        source_type=SourceType.DOCUMENT,
        content_hash="test-hash",
        minio_path="test/path/test.pdf"
    )
    db.add(document)
    db.commit()
    
    # 验证文档创建
    created_doc = db.query(Document).filter(Document.id == "test-doc-1").first()
    assert created_doc is not None
    assert created_doc.file_name == "test.pdf"
    assert created_doc.category == "test"
    assert created_doc.collection == "knowledge_base"
    assert created_doc.source_type == SourceType.DOCUMENT
    assert created_doc.content_hash == "test-hash"
    assert created_doc.minio_path == "test/path/test.pdf"


def test_document_metadata(db: Session):
    """测试文档元数据"""
    # 创建文档
    document = Document(
        id="test-doc-2",
        file_name="test.md",
        category="test",
        collection="knowledge_base",
        source_type=SourceType.DOCUMENT,
        content_hash="test-hash-2",
        minio_path="test/path/test.md"
    )
    db.add(document)
    
    # 添加元数据
    metadata = DocumentMetadata(
        document_id="test-doc-2",
        key="author",
        value="test author"
    )
    db.add(metadata)
    db.commit()
    
    # 验证元数据
    created_doc = db.query(Document).filter(Document.id == "test-doc-2").first()
    assert len(created_doc.metadata_items) == 1
    assert created_doc.metadata_items[0].key == "author"
    assert created_doc.metadata_items[0].value == "test author"


def test_document_processing(db: Session):
    """测试文档处理状态"""
    # 创建文档
    document = Document(
        id="test-doc-3",
        file_name="test.txt",
        category="test",
        collection="knowledge_base",
        source_type=SourceType.DOCUMENT,
        content_hash="test-hash-3",
        minio_path="test/path/test.txt"
    )
    db.add(document)
    
    # 创建处理状态
    processing = DocumentProcessing(
        document_id="test-doc-3",
        task_id="test-task-3",
        status=DocumentStatus.PENDING,
        progress=0,
        total=100
    )
    db.add(processing)
    db.commit()
    
    # 验证处理状态
    created_doc = db.query(Document).filter(Document.id == "test-doc-3").first()
    assert created_doc.processing is not None
    assert created_doc.processing.task_id == "test-task-3"
    assert created_doc.processing.status == DocumentStatus.PENDING
    assert created_doc.processing.progress == 0
    assert created_doc.processing.total == 100


def test_document_processing_update(db: Session):
    """测试文档处理状态更新"""
    # 创建文档和处理状态
    document = Document(
        id="test-doc-4",
        file_name="test.pdf",
        category="test",
        collection="knowledge_base",
        source_type=SourceType.DOCUMENT,
        content_hash="test-hash-4",
        minio_path="test/path/test.pdf"
    )
    db.add(document)
    
    processing = DocumentProcessing(
        document_id="test-doc-4",
        task_id="test-task-4",
        status=DocumentStatus.PENDING,
        progress=0,
        total=100
    )
    db.add(processing)
    db.commit()
    
    # 更新处理状态
    processing.status = DocumentStatus.PROCESSING
    processing.progress = 50
    processing.current_step = "embedding"
    db.commit()
    
    # 验证更新
    updated_processing = db.query(DocumentProcessing).filter(DocumentProcessing.document_id == "test-doc-4").first()
    assert updated_processing.status == DocumentStatus.PROCESSING
    assert updated_processing.progress == 50
    assert updated_processing.current_step == "embedding"
