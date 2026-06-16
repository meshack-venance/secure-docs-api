from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from audits.models import AuditLog
from documents.models import Document


User = get_user_model()


def response_body(response):
    return response.json()


@override_settings(ALLOWED_HOSTS=["localhost", "testserver"])
class DocumentAPITests(APITestCase):
    def setUp(self):
        self.media_root = TemporaryDirectory()
        self.override_media = override_settings(MEDIA_ROOT=self.media_root.name)
        self.override_media.enable()
        self.addCleanup(self.override_media.disable)
        self.addCleanup(self.media_root.cleanup)

        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            email="user@example.com",
            password=self.password,
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password=self.password,
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password=self.password,
        )
        self.officer = User.objects.create_user(
            email="officer@example.com",
            password=self.password,
            role=User.Role.OFFICER,
        )
        self.list_url = reverse("documents:document-list")

    def authenticate(self, user):
        response = self.client.post(
            reverse("authentication:login"),
            {"email": user.email, "password": self.password},
            format="json",
            HTTP_HOST="localhost",
        )
        token = response_body(response)["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def upload_file(self, name="document.txt", content=b"test document"):
        return SimpleUploadedFile(name, content, content_type="text/plain")

    def create_document(self, uploaded_by, title="Document"):
        return Document.objects.create(
            title=title,
            file=self.upload_file(),
            uploaded_by=uploaded_by,
        )

    def detail_url(self, document, action=None):
        name = "documents:document-detail"
        if action:
            name = f"documents:document-{action}"

        return reverse(name, kwargs={"pk": document.id})

    def review_url(self, document):
        return self.detail_url(document, "review")

    def verify_url(self, verification_code):
        return reverse("verify-document", kwargs={"verification_code": verification_code})

    def test_authenticated_user_can_upload_document(self):
        self.authenticate(self.user)

        response = self.client.post(
            self.list_url,
            {
                "title": "Degree Certificate",
                "description": "Bachelor certificate",
                "file": self.upload_file(),
            },
            format="multipart",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "Document uploaded successfully")
        self.assertEqual(Document.objects.count(), 1)
        document = Document.objects.first()
        self.assertEqual(document.uploaded_by, self.user)
        audit_log = AuditLog.objects.get(action=AuditLog.Action.DOCUMENT_UPLOADED)
        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.entity, "Document")
        self.assertEqual(audit_log.entity_id, document.id)
        self.assertEqual(audit_log.metadata["status"], Document.Status.PENDING)

    def test_document_type_is_not_accepted_from_upload_body(self):
        self.authenticate(self.user)

        response = self.client.post(
            self.list_url,
            {
                "title": "Degree Certificate",
                "description": "Bachelor certificate",
                "document_type": "Certificate",
                "file": self.upload_file(),
            },
            format="multipart",
            HTTP_HOST="localhost",
        )

        document = Document.objects.get()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(document.document_type, "")

    def test_anonymous_user_cannot_upload_document(self):
        response = self.client.post(
            self.list_url,
            {
                "title": "Anonymous Upload",
                "file": self.upload_file(),
            },
            format="multipart",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertIsNone(body["data"])

    def test_user_can_list_only_own_documents(self):
        own_document = self.create_document(self.user, title="Mine")
        self.create_document(self.other_user, title="Other")
        self.authenticate(self.user)

        response = self.client.get(self.list_url, HTTP_HOST="localhost")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "Documents fetched successfully")
        document_ids = [item["id"] for item in body["data"]["results"]]
        self.assertEqual(document_ids, [own_document.id])

    def test_admin_can_list_all_documents(self):
        first_document = self.create_document(self.user, title="First")
        second_document = self.create_document(self.other_user, title="Second")
        self.authenticate(self.admin)

        response = self.client.get(self.list_url, HTTP_HOST="localhost")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response_body(response)
        document_ids = {item["id"] for item in body["data"]["results"]}
        self.assertEqual(document_ids, {first_document.id, second_document.id})

    def test_invalid_status_filter_returns_secure_docs_exception(self):
        self.authenticate(self.user)

        response = self.client.get(
            self.list_url,
            {"status": "INVALID"},
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertEqual(body["message"], "Invalid document status filter")
        self.assertEqual(body["status"], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(body["error"], "INVALID_DOCUMENT_STATUS")
        self.assertIsNone(body["data"])
        self.assertNotIn("errors", body)

    def test_document_receives_verification_code_and_pending_status(self):
        document = self.create_document(self.user)

        self.assertEqual(document.status, Document.Status.PENDING)
        self.assertEqual(len(document.verification_code), 9)

    def test_user_can_retrieve_own_document(self):
        document = self.create_document(self.user)
        self.authenticate(self.user)

        response = self.client.get(
            self.detail_url(document),
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "Document fetched successfully")
        self.assertEqual(body["data"]["id"], document.id)

    def test_user_can_patch_own_document(self):
        document = self.create_document(self.user)
        self.authenticate(self.user)

        response = self.client.patch(
            self.detail_url(document),
            {"description": "Updated from PATCH only."},
            format="json",
            HTTP_HOST="localhost",
        )

        document.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "Document updated successfully")
        self.assertEqual(body["data"]["description"], "Updated from PATCH only.")
        self.assertEqual(document.description, "Updated from PATCH only.")

    def test_put_document_update_is_not_allowed(self):
        document = self.create_document(self.user)
        self.authenticate(self.user)

        response = self.client.put(
            self.detail_url(document),
            {
                "title": "Full replacement",
                "description": "PUT should not be allowed.",
                "file": self.upload_file(),
            },
            format="multipart",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertEqual(body["message"], 'Method "PUT" not allowed.')

    def test_user_cannot_retrieve_another_users_document(self):
        document = self.create_document(self.other_user)
        self.authenticate(self.user)

        response = self.client.get(
            self.detail_url(document),
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertIsNone(body["data"])

    def test_user_can_delete_own_document(self):
        document = self.create_document(self.user)
        self.authenticate(self.user)

        response = self.client.delete(
            self.detail_url(document),
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "Document deleted successfully")
        self.assertIsNone(body["data"])
        self.assertFalse(Document.objects.filter(id=document.id).exists())
        audit_log = AuditLog.objects.get(action=AuditLog.Action.DOCUMENT_DELETED)
        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.entity_id, document.id)
        self.assertEqual(audit_log.metadata["title"], document.title)

    def test_officer_can_start_document_review(self):
        document = self.create_document(self.user)
        self.authenticate(self.officer)

        response = self.client.post(
            self.review_url(document),
            {
                "action": "START_REVIEW",
                "review_notes": "Initial review started.",
            },
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "Document review started successfully")
        self.assertEqual(body["data"]["status"], Document.Status.UNDER_REVIEW)
        self.assertEqual(body["data"]["reviewed_by_email"], self.officer.email)
        self.assertEqual(body["data"]["review_notes"], "Initial review started.")
        audit_log = AuditLog.objects.get(action=AuditLog.Action.DOCUMENT_REVIEW_STARTED)
        self.assertEqual(audit_log.user, self.officer)
        self.assertEqual(audit_log.entity_id, document.id)
        self.assertEqual(audit_log.metadata["status"], Document.Status.UNDER_REVIEW)

    def test_officer_can_approve_pending_document(self):
        document = self.create_document(self.user)
        self.authenticate(self.officer)

        response = self.client.post(
            self.review_url(document),
            {
                "action": "APPROVE",
                "review_notes": "Document details match official records.",
            },
            format="json",
            HTTP_HOST="localhost",
        )

        document.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "Document approved successfully")
        self.assertEqual(body["data"]["status"], Document.Status.APPROVED)
        self.assertEqual(document.status, Document.Status.APPROVED)
        self.assertEqual(document.reviewed_by, self.officer)
        self.assertIsNotNone(document.reviewed_at)
        self.assertEqual(document.review_notes, "Document details match official records.")
        audit_log = AuditLog.objects.get(action=AuditLog.Action.DOCUMENT_APPROVED)
        self.assertEqual(audit_log.user, self.officer)
        self.assertEqual(audit_log.entity_id, document.id)
        self.assertEqual(audit_log.metadata["review_notes"], document.review_notes)

    def test_normal_user_cannot_approve_document(self):
        document = self.create_document(self.user)
        self.authenticate(self.user)

        response = self.client.post(
            self.review_url(document),
            {
                "action": "APPROVE",
                "review_notes": "Trying to self approve.",
            },
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertEqual(body["message"], "Only admins and officers can review documents")
        self.assertEqual(body["error"], "DOCUMENT_REVIEW_FORBIDDEN")
        self.assertNotIn("errors", body)

    def test_reject_requires_review_notes(self):
        document = self.create_document(self.user)
        self.authenticate(self.officer)

        response = self.client.post(
            self.review_url(document),
            {"action": "REJECT"},
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertIn("review_notes", body["errors"])

    def test_officer_can_reject_pending_document(self):
        document = self.create_document(self.user)
        self.authenticate(self.officer)

        response = self.client.post(
            self.review_url(document),
            {
                "action": "REJECT",
                "review_notes": "Certificate number could not be verified.",
            },
            format="json",
            HTTP_HOST="localhost",
        )

        document.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "Document rejected successfully")
        self.assertEqual(body["data"]["status"], Document.Status.REJECTED)
        self.assertEqual(document.status, Document.Status.REJECTED)
        self.assertEqual(document.reviewed_by, self.officer)
        self.assertEqual(document.review_notes, "Certificate number could not be verified.")
        audit_log = AuditLog.objects.get(action=AuditLog.Action.DOCUMENT_REJECTED)
        self.assertEqual(audit_log.user, self.officer)
        self.assertEqual(audit_log.entity_id, document.id)
        self.assertEqual(audit_log.metadata["status"], Document.Status.REJECTED)

    def test_approved_document_cannot_be_rejected(self):
        document = self.create_document(self.user)
        document.status = Document.Status.APPROVED
        document.save(update_fields=("status", "updated_at"))
        self.authenticate(self.officer)

        response = self.client.post(
            self.review_url(document),
            {
                "action": "REJECT",
                "review_notes": "Trying to reject after approval.",
            },
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertEqual(body["message"], "Approved documents cannot be reviewed again")
        self.assertEqual(body["error"], "DOCUMENT_ALREADY_APPROVED")
        self.assertNotIn("errors", body)

    def test_rejected_document_cannot_be_approved(self):
        document = self.create_document(self.user)
        document.status = Document.Status.REJECTED
        document.save(update_fields=("status", "updated_at"))
        self.authenticate(self.officer)

        response = self.client.post(
            self.review_url(document),
            {
                "action": "APPROVE",
                "review_notes": "Trying to approve after rejection.",
            },
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertEqual(body["message"], "Rejected documents cannot be reviewed again")
        self.assertEqual(body["error"], "DOCUMENT_ALREADY_REJECTED")
        self.assertNotIn("errors", body)

    def test_invalid_review_action_returns_bad_request(self):
        document = self.create_document(self.user)
        self.authenticate(self.officer)

        response = self.client.post(
            self.review_url(document),
            {"action": "INVALID", "review_notes": "Bad action."},
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertIn("action", body["errors"])

    def test_public_can_verify_approved_document(self):
        document = self.create_document(self.user, title="Degree Certificate")
        document.status = Document.Status.APPROVED
        document.reviewed_by = self.officer
        document.reviewed_at = timezone.now()
        document.save(update_fields=("status", "reviewed_by", "reviewed_at", "updated_at"))

        response = self.client.get(
            self.verify_url(document.verification_code),
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response_body(response)
        self.assertTrue(body["success"])
        self.assertEqual(body["message"], "Document verified successfully")
        self.assertTrue(body["data"]["verified"])
        self.assertEqual(body["data"]["title"], "Degree Certificate")
        self.assertEqual(body["data"]["verification_code"], document.verification_code)
        self.assertEqual(body["data"]["status"], Document.Status.APPROVED)
        self.assertNotIn("file", body["data"])
        self.assertNotIn("uploaded_by_email", body["data"])
        self.assertNotIn("reviewed_by_email", body["data"])
        self.assertNotIn("review_notes", body["data"])
        audit_log = AuditLog.objects.get(
            action=AuditLog.Action.DOCUMENT_VERIFICATION_SUCCEEDED
        )
        self.assertIsNone(audit_log.user)
        self.assertEqual(audit_log.entity_id, document.id)
        self.assertEqual(audit_log.metadata["result"], "VERIFIED")

    def test_public_cannot_verify_pending_document(self):
        document = self.create_document(self.user)

        response = self.client.get(
            self.verify_url(document.verification_code),
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertEqual(body["message"], "Document is not approved for public verification")
        self.assertEqual(body["error"], "DOCUMENT_NOT_APPROVED_FOR_VERIFICATION")
        self.assertIsNone(body["data"])
        audit_log = AuditLog.objects.get(action=AuditLog.Action.DOCUMENT_VERIFICATION_FAILED)
        self.assertIsNone(audit_log.user)
        self.assertEqual(audit_log.entity_id, document.id)
        self.assertEqual(audit_log.metadata["result"], "FAILED")

    def test_public_cannot_verify_rejected_document(self):
        document = self.create_document(self.user)
        document.status = Document.Status.REJECTED
        document.save(update_fields=("status", "updated_at"))

        response = self.client.get(
            self.verify_url(document.verification_code),
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertEqual(body["error"], "DOCUMENT_NOT_APPROVED_FOR_VERIFICATION")

    def test_public_unknown_verification_code_returns_not_found(self):
        response = self.client.get(
            self.verify_url("UNKNOWN123"),
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        body = response_body(response)
        self.assertFalse(body["success"])
        self.assertEqual(body["message"], "Document could not be verified")
        self.assertEqual(body["error"], "DOCUMENT_VERIFICATION_NOT_FOUND")
        self.assertIsNone(body["data"])
        audit_log = AuditLog.objects.get(action=AuditLog.Action.DOCUMENT_VERIFICATION_FAILED)
        self.assertIsNone(audit_log.user)
        self.assertEqual(audit_log.entity_id, 0)
        self.assertEqual(audit_log.metadata["verification_code"], "UNKNOWN123")
