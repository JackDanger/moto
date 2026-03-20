"""RekognitionBackend class with methods for supported APIs."""

import string
import time
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.utils import unix_time
from moto.moto_api._internal import mock_random as random

from .exceptions import (
    ResourceAlreadyExistsException,
    ResourceInUseException,
    ResourceNotFoundException,
)


def _random_id(length: int = 64) -> str:
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(length)
    )


def _random_uuid() -> str:
    return str(random.uuid4())


def _make_face(
    face_id: str,
    image_id: str,
    external_image_id: Optional[str] = None,
    confidence: float = 99.99,
) -> dict[str, Any]:
    face: dict[str, Any] = {
        "FaceId": face_id,
        "BoundingBox": {
            "Width": 0.5521978139877319,
            "Top": 0.1203877404332161,
            "Left": 0.23626373708248138,
            "Height": 0.3126954436302185,
        },
        "ImageId": image_id,
        "Confidence": confidence,
        "Landmarks": [
            {"Type": "eyeLeft", "X": 0.4800, "Y": 0.2343},
            {"Type": "eyeRight", "X": 0.6380, "Y": 0.1922},
            {"Type": "nose", "X": 0.6197, "Y": 0.3800},
            {"Type": "mouthLeft", "X": 0.5283, "Y": 0.6190},
            {"Type": "mouthRight", "X": 0.6604, "Y": 0.5830},
        ],
        "Pose": {"Roll": -5.06, "Yaw": 18.04, "Pitch": 12.57},
        "Quality": {"Brightness": 83.42, "Sharpness": 67.23},
    }
    if external_image_id is not None:
        face["ExternalImageId"] = external_image_id
    return face


class RekognitionBackend(BaseBackend):
    """Implementation of Rekognition APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        # Collections: collection_id -> {faces: {face_id -> face_record}, ...}
        self._collections: dict[str, dict[str, Any]] = {}
        # Projects: project_arn -> project_dict
        self._projects: dict[str, dict[str, Any]] = {}
        # Project versions: version_arn -> version_dict
        self._project_versions: dict[str, dict[str, Any]] = {}
        # Datasets: dataset_arn -> dataset_dict
        self._datasets: dict[str, dict[str, Any]] = {}
        # Stream processors: name -> processor_dict
        self._stream_processors: dict[str, dict[str, Any]] = {}

    def _collection_arn(self, collection_id: str) -> str:
        return (
            f"arn:aws:rekognition:{self.region_name}:{self.account_id}:"
            f"collection/{collection_id}"
        )

    def _project_arn(self, project_name: str) -> str:
        return (
            f"arn:aws:rekognition:{self.region_name}:{self.account_id}:"
            f"project/{project_name}/{int(time.time() * 1000)}"
        )

    def _project_version_arn(self, project_name: str, version_name: str) -> str:
        return (
            f"arn:aws:rekognition:{self.region_name}:{self.account_id}:"
            f"project/{project_name}/version/{version_name}/{int(time.time() * 1000)}"
        )

    def _dataset_arn(self, project_name: str, dataset_type: str) -> str:
        return (
            f"arn:aws:rekognition:{self.region_name}:{self.account_id}:"
            f"project/{project_name}/dataset/{dataset_type}/{int(time.time() * 1000)}"
        )

    def _stream_processor_arn(self, name: str) -> str:
        return (
            f"arn:aws:rekognition:{self.region_name}:{self.account_id}:"
            f"streamprocessor/{name}"
        )

    # ---- Collections ----

    def create_collection(self, collection_id: str) -> dict[str, Any]:
        if collection_id in self._collections:
            raise ResourceAlreadyExistsException(
                f"A collection with the specified ID already exists in this account. "
                f"CollectionId: {collection_id}"
            )
        arn = self._collection_arn(collection_id)
        self._collections[collection_id] = {
            "CollectionId": collection_id,
            "CollectionArn": arn,
            "FaceModelVersion": "6.0",
            "CreationTimestamp": unix_time(),
            "faces": {},  # face_id -> face_record (internal)
            "users": [],  # list of user dicts (UserId, UserStatus)
        }
        return {
            "StatusCode": 200,
            "CollectionArn": arn,
            "FaceModelVersion": "6.0",
        }

    def delete_collection(self, collection_id: str) -> dict[str, Any]:
        if collection_id not in self._collections:
            raise ResourceNotFoundException(
                f"The collection id: {collection_id} does not exist"
            )
        del self._collections[collection_id]
        return {"StatusCode": 200}

    def describe_collection(self, collection_id: str) -> dict[str, Any]:
        if collection_id not in self._collections:
            raise ResourceNotFoundException(
                f"The collection id: {collection_id} does not exist"
            )
        col = self._collections[collection_id]
        return {
            "FaceCount": len(col["faces"]),
            "FaceModelVersion": col["FaceModelVersion"],
            "CollectionARN": col["CollectionArn"],
            "CreationTimestamp": col["CreationTimestamp"],
        }

    def list_collections(
        self, max_results: int = 4096, next_token: Optional[str] = None
    ) -> dict[str, Any]:
        all_ids = sorted(self._collections.keys())
        start = 0
        if next_token:
            try:
                start = all_ids.index(next_token)
            except ValueError:
                start = 0
        end = start + max_results
        page = all_ids[start:end]
        result: dict[str, Any] = {
            "CollectionIds": page,
            "FaceModelVersions": [
                self._collections[cid]["FaceModelVersion"] for cid in page
            ],
        }
        if end < len(all_ids):
            result["NextToken"] = all_ids[end]
        return result

    def index_faces(
        self,
        collection_id: str,
        image: dict[str, Any],
        external_image_id: Optional[str] = None,
        max_faces: int = 20,
        quality_filter: str = "AUTO",
        detection_attributes: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        if collection_id not in self._collections:
            raise ResourceNotFoundException(
                f"The collection id: {collection_id} does not exist"
            )
        col = self._collections[collection_id]
        # Generate a synthetic face record
        face_id = _random_uuid()
        image_id = _random_uuid()
        face = _make_face(face_id, image_id, external_image_id)
        col["faces"][face_id] = face

        face_record = {
            "Face": face,
            "FaceDetail": {
                "BoundingBox": face["BoundingBox"],
                "Landmarks": face["Landmarks"],
                "Pose": face["Pose"],
                "Quality": face["Quality"],
                "Confidence": face["Confidence"],
            },
        }
        return {
            "FaceRecords": [face_record],
            "FaceModelVersion": col["FaceModelVersion"],
            "UnindexedFaces": [],
            "OrientationCorrection": "ROTATE_0",
        }

    def list_faces(
        self,
        collection_id: str,
        max_results: int = 4096,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        if collection_id not in self._collections:
            raise ResourceNotFoundException(
                f"The collection id: {collection_id} does not exist"
            )
        col = self._collections[collection_id]
        faces = list(col["faces"].values())
        start = 0
        if next_token:
            for i, f in enumerate(faces):
                if f["FaceId"] == next_token:
                    start = i
                    break
        end = start + max_results
        page = faces[start:end]
        result: dict[str, Any] = {
            "Faces": page,
            "FaceModelVersion": col["FaceModelVersion"],
        }
        if end < len(faces):
            result["NextToken"] = faces[end]["FaceId"]
        return result

    def list_users(
        self,
        collection_id: str,
        max_results: int = 100,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        if collection_id not in self._collections:
            raise ResourceNotFoundException(
                f"The collection id: {collection_id} does not exist"
            )
        col = self._collections[collection_id]
        users = col.get("users", [])
        start = int(next_token) if next_token else 0
        end = start + max_results
        page = users[start:end]
        result: dict[str, Any] = {"Users": page, "NextToken": None}
        if end < len(users):
            result["NextToken"] = str(end)
        return result

    def create_user(
        self,
        collection_id: str,
        user_id: str,
        client_request_token: Optional[str] = None,
    ) -> dict[str, Any]:
        if collection_id not in self._collections:
            raise ResourceNotFoundException(
                f"The collection id: {collection_id} does not exist"
            )
        col = self._collections[collection_id]
        users = col.get("users", [])
        for u in users:
            if u["UserId"] == user_id:
                raise ResourceAlreadyExistsException(
                    f"A user with the specified ID already exists. UserId: {user_id}"
                )
        users.append({"UserId": user_id, "UserStatus": "ACTIVE"})
        col["users"] = users
        return {}

    def delete_user(
        self,
        collection_id: str,
        user_id: str,
        client_request_token: Optional[str] = None,
    ) -> dict[str, Any]:
        if collection_id not in self._collections:
            raise ResourceNotFoundException(
                f"The collection id: {collection_id} does not exist"
            )
        col = self._collections[collection_id]
        users = col.get("users", [])
        original_count = len(users)
        col["users"] = [u for u in users if u["UserId"] != user_id]
        if len(col["users"]) == original_count:
            raise ResourceNotFoundException(
                f"The user id: {user_id} does not exist in the collection"
            )
        return {}

    def search_users(
        self,
        collection_id: str,
        user_id: Optional[str] = None,
        face_id: Optional[str] = None,
        max_users: int = 100,
        user_match_threshold: float = 80.0,
        quality_filter: str = "AUTO",
    ) -> dict[str, Any]:
        if collection_id not in self._collections:
            raise ResourceNotFoundException(
                f"The collection id: {collection_id} does not exist"
            )
        col = self._collections[collection_id]
        # Return all users as matches (synthetic similarity)
        users = col.get("users", [])
        matches = []
        for user in users[:max_users]:
            if user_id and user["UserId"] == user_id:
                continue  # exclude the searched user itself
            matches.append(
                {
                    "User": {"UserId": user["UserId"], "UserStatus": user["UserStatus"]},
                    "Similarity": 99.99,
                    "MatchConfidence": 99.99,
                }
            )
        result: dict[str, Any] = {
            "UserMatches": matches,
            "FaceModelVersion": col["FaceModelVersion"],
        }
        if user_id:
            result["SearchedUser"] = {"UserId": user_id}
        if face_id:
            result["SearchedFace"] = {"FaceId": face_id}
        return result

    def search_users_by_image(
        self,
        collection_id: str,
        image: dict[str, Any],
        max_users: int = 100,
        quality_filter: str = "AUTO",
        user_match_threshold: float = 80.0,
    ) -> dict[str, Any]:
        if collection_id not in self._collections:
            raise ResourceNotFoundException(
                f"The collection id: {collection_id} does not exist"
            )
        col = self._collections[collection_id]
        users = col.get("users", [])
        matches = []
        for user in users[:max_users]:
            matches.append(
                {
                    "User": {"UserId": user["UserId"], "UserStatus": user["UserStatus"]},
                    "Similarity": 99.99,
                    "MatchConfidence": 99.99,
                }
            )
        return {
            "UserMatches": matches,
            "FaceModelVersion": col["FaceModelVersion"],
            "SearchedFace": {
                "FaceDetail": {
                    "BoundingBox": {
                        "Width": 0.55,
                        "Top": 0.12,
                        "Left": 0.24,
                        "Height": 0.31,
                    },
                    "Confidence": 99.99,
                }
            },
        }

    def associate_faces(
        self,
        collection_id: str,
        user_id: str,
        face_ids: list[str],
        user_matching_threshold: float = 75.0,
        client_request_token: Optional[str] = None,
    ) -> dict[str, Any]:
        if collection_id not in self._collections:
            raise ResourceNotFoundException(
                f"The collection id: {collection_id} does not exist"
            )
        col = self._collections[collection_id]
        users = col.get("users", [])
        user = next((u for u in users if u["UserId"] == user_id), None)
        if user is None:
            raise ResourceNotFoundException(
                f"The user id: {user_id} does not exist in the collection"
            )
        # Track associated faces on the user
        user.setdefault("AssociatedFaces", [])
        associated = []
        unsuccessful = []
        for face_id in face_ids:
            if face_id in col["faces"]:
                if face_id not in user["AssociatedFaces"]:
                    user["AssociatedFaces"].append(face_id)
                associated.append({"FaceId": face_id})
            else:
                unsuccessful.append(
                    {"FaceId": face_id, "Reasons": ["FACE_NOT_FOUND"], "Confidence": 0.0}
                )
        return {
            "AssociatedFaces": associated,
            "UnsuccessfulFaceAssociations": unsuccessful,
            "UserStatus": user["UserStatus"],
        }

    def disassociate_faces(
        self,
        collection_id: str,
        user_id: str,
        face_ids: list[str],
        client_request_token: Optional[str] = None,
    ) -> dict[str, Any]:
        if collection_id not in self._collections:
            raise ResourceNotFoundException(
                f"The collection id: {collection_id} does not exist"
            )
        col = self._collections[collection_id]
        users = col.get("users", [])
        user = next((u for u in users if u["UserId"] == user_id), None)
        if user is None:
            raise ResourceNotFoundException(
                f"The user id: {user_id} does not exist in the collection"
            )
        associated = user.get("AssociatedFaces", [])
        disassociated = []
        unsuccessful = []
        for face_id in face_ids:
            if face_id in associated:
                associated.remove(face_id)
                disassociated.append({"FaceId": face_id})
            else:
                unsuccessful.append(
                    {
                        "FaceId": face_id,
                        "Reasons": ["ASSOCIATED_TO_A_DIFFERENT_USER"],
                        "Confidence": 0.0,
                    }
                )
        user["AssociatedFaces"] = associated
        return {
            "DisassociatedFaces": disassociated,
            "UnsuccessfulFaceDisassociations": unsuccessful,
            "UserStatus": user["UserStatus"],
        }

    def delete_faces(self, collection_id: str, face_ids: list[str]) -> dict[str, Any]:
        if collection_id not in self._collections:
            raise ResourceNotFoundException(
                f"The collection id: {collection_id} does not exist"
            )
        col = self._collections[collection_id]
        deleted = []
        for fid in face_ids:
            if fid in col["faces"]:
                del col["faces"][fid]
                deleted.append(fid)
        return {"DeletedFaces": deleted}

    def search_faces(
        self,
        collection_id: str,
        face_id: str,
        max_faces: int = 80,
        face_match_threshold: float = 80.0,
    ) -> dict[str, Any]:
        if collection_id not in self._collections:
            raise ResourceNotFoundException(
                f"The collection id: {collection_id} does not exist"
            )
        col = self._collections[collection_id]
        if face_id not in col["faces"]:
            raise ResourceNotFoundException(
                f"The face id: {face_id} does not exist in the collection"
            )
        searched_face = col["faces"][face_id]
        # Return other faces as matches with high similarity
        matches = []
        for fid, face in col["faces"].items():
            if fid == face_id:
                continue
            matches.append({"Similarity": 99.99, "Face": face})
            if len(matches) >= max_faces:
                break
        return {
            "SearchedFaceId": face_id,
            "FaceMatches": matches,
            "FaceModelVersion": col["FaceModelVersion"],
            "SearchedFace": {
                "FaceId": face_id,
                "BoundingBox": searched_face["BoundingBox"],
            },
        }

    def search_faces_by_image(
        self,
        collection_id: str,
        image: dict[str, Any],
        max_faces: int = 80,
        face_match_threshold: float = 80.0,
    ) -> dict[str, Any]:
        if collection_id not in self._collections:
            raise ResourceNotFoundException(
                f"The collection id: {collection_id} does not exist"
            )
        col = self._collections[collection_id]
        # Return all indexed faces as matches
        matches = []
        for face in list(col["faces"].values())[:max_faces]:
            matches.append({"Similarity": 99.99, "Face": face})
        return {
            "SearchedFaceBoundingBox": {
                "Width": 0.55,
                "Top": 0.12,
                "Left": 0.24,
                "Height": 0.31,
            },
            "SearchedFaceConfidence": 99.99,
            "FaceMatches": matches,
            "FaceModelVersion": col["FaceModelVersion"],
        }

    # ---- Projects ----

    def create_project(self, project_name: str) -> dict[str, Any]:
        # Check for duplicate by name
        for proj in self._projects.values():
            if proj["ProjectName"] == project_name:
                raise ResourceAlreadyExistsException(
                    f"A project with the name {project_name} already exists"
                )
        arn = self._project_arn(project_name)
        project = {
            "ProjectArn": arn,
            "ProjectName": project_name,
            "CreationTimestamp": unix_time(),
            "Status": "CREATED",
            "Datasets": [],
        }
        self._projects[arn] = project
        return {"ProjectArn": arn}

    def describe_projects(
        self,
        project_names: Optional[list[str]] = None,
        max_results: int = 100,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        projects = list(self._projects.values())
        if project_names:
            projects = [p for p in projects if p["ProjectName"] in project_names]
        # Simple pagination
        start = 0
        if next_token:
            for i, p in enumerate(projects):
                if p["ProjectArn"] == next_token:
                    start = i
                    break
        end = start + max_results
        page = projects[start:end]
        descriptions = []
        for p in page:
            desc = {
                "ProjectArn": p["ProjectArn"],
                "CreationTimestamp": p["CreationTimestamp"],
                "Status": p["Status"],
                "Datasets": p.get("Datasets", []),
            }
            descriptions.append(desc)
        result: dict[str, Any] = {"ProjectDescriptions": descriptions}
        if end < len(projects):
            result["NextToken"] = projects[end]["ProjectArn"]
        return result

    def delete_project(self, project_arn: str) -> dict[str, Any]:
        if project_arn not in self._projects:
            raise ResourceNotFoundException(
                f"The project with ARN {project_arn} does not exist"
            )
        # Check no running versions
        for v in self._project_versions.values():
            if v["ProjectArn"] == project_arn and v["Status"] == "RUNNING":
                raise ResourceInUseException(
                    "The project has running versions and cannot be deleted"
                )
        del self._projects[project_arn]
        return {"Status": "DELETING"}

    def create_project_version(
        self,
        project_arn: str,
        version_name: str,
        output_config: dict[str, Any],
        training_data: Optional[dict[str, Any]] = None,
        testing_data: Optional[dict[str, Any]] = None,
        version_description: Optional[str] = None,
    ) -> dict[str, Any]:
        if project_arn not in self._projects:
            raise ResourceNotFoundException(
                f"The project with ARN {project_arn} does not exist"
            )
        project = self._projects[project_arn]
        project_name = project["ProjectName"]

        # Check for duplicate version name under this project
        for v in self._project_versions.values():
            if v["ProjectArn"] == project_arn and v["VersionName"] == version_name:
                raise ResourceAlreadyExistsException(
                    f"A project version with name {version_name} already exists"
                )

        version_arn = self._project_version_arn(project_name, version_name)
        version = {
            "ProjectVersionArn": version_arn,
            "ProjectArn": project_arn,
            "VersionName": version_name,
            "CreationTimestamp": unix_time(),
            "Status": "TRAINING_COMPLETED",
            "StatusMessage": "Training completed successfully",
            "OutputConfig": output_config,
            "TrainingDataResult": {"Input": training_data or {}},
            "TestingDataResult": {"Input": testing_data or {}},
            "VersionDescription": version_description or "",
            "BillableTrainingTimeInSeconds": 3600,
            "TrainingEndTimestamp": unix_time(),
        }
        self._project_versions[version_arn] = version
        return {"ProjectVersionArn": version_arn}

    def describe_project_versions(
        self,
        project_arn: str,
        version_names: Optional[list[str]] = None,
        max_results: int = 100,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        if project_arn not in self._projects:
            raise ResourceNotFoundException(
                f"The project with ARN {project_arn} does not exist"
            )
        versions = [
            v for v in self._project_versions.values() if v["ProjectArn"] == project_arn
        ]
        if version_names:
            versions = [v for v in versions if v["VersionName"] in version_names]

        start = 0
        if next_token:
            for i, v in enumerate(versions):
                if v["ProjectVersionArn"] == next_token:
                    start = i
                    break
        end = start + max_results
        page = versions[start:end]
        descriptions = []
        for v in page:
            desc = {
                "ProjectVersionArn": v["ProjectVersionArn"],
                "CreationTimestamp": v["CreationTimestamp"],
                "Status": v["Status"],
                "StatusMessage": v.get("StatusMessage", ""),
                "OutputConfig": v.get("OutputConfig", {}),
                "BillableTrainingTimeInSeconds": v.get(
                    "BillableTrainingTimeInSeconds", 0
                ),
                "TrainingEndTimestamp": v.get("TrainingEndTimestamp", 0),
            }
            descriptions.append(desc)
        result: dict[str, Any] = {"ProjectVersionDescriptions": descriptions}
        if end < len(versions):
            result["NextToken"] = versions[end]["ProjectVersionArn"]
        return result

    def delete_project_version(self, project_version_arn: str) -> dict[str, Any]:
        if project_version_arn not in self._project_versions:
            raise ResourceNotFoundException(
                f"The project version with ARN {project_version_arn} does not exist"
            )
        version = self._project_versions[project_version_arn]
        if version["Status"] == "RUNNING":
            raise ResourceInUseException(
                "The project version is running and cannot be deleted"
            )
        del self._project_versions[project_version_arn]
        return {"Status": "DELETING"}

    def start_project_version(
        self,
        project_version_arn: str,
        min_inference_units: int,
        max_inference_units: Optional[int] = None,
    ) -> dict[str, Any]:
        if project_version_arn not in self._project_versions:
            raise ResourceNotFoundException(
                f"The project version with ARN {project_version_arn} does not exist"
            )
        version = self._project_versions[project_version_arn]
        version["Status"] = "RUNNING"
        version["MinInferenceUnits"] = min_inference_units
        if max_inference_units:
            version["MaxInferenceUnits"] = max_inference_units
        return {"Status": "STARTING"}

    def stop_project_version(self, project_version_arn: str) -> dict[str, Any]:
        if project_version_arn not in self._project_versions:
            raise ResourceNotFoundException(
                f"The project version with ARN {project_version_arn} does not exist"
            )
        version = self._project_versions[project_version_arn]
        version["Status"] = "STOPPED"
        return {"Status": "STOPPING"}

    # ---- Custom Labels (DetectCustomLabels already exists, adding datasets) ----

    def create_dataset(
        self,
        project_arn: str,
        dataset_type: str,
        dataset_source: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        if project_arn not in self._projects:
            raise ResourceNotFoundException(
                f"The project with ARN {project_arn} does not exist"
            )
        project = self._projects[project_arn]
        project_name = project["ProjectName"]

        # Check for duplicate dataset type under this project
        for ds in self._datasets.values():
            if ds["ProjectArn"] == project_arn and ds["DatasetType"] == dataset_type:
                raise ResourceAlreadyExistsException(
                    f"A {dataset_type} dataset already exists for project {project_arn}"
                )

        dataset_arn = self._dataset_arn(project_name, dataset_type)
        dataset = {
            "DatasetArn": dataset_arn,
            "ProjectArn": project_arn,
            "DatasetType": dataset_type,
            "CreationTimestamp": unix_time(),
            "LastUpdatedTimestamp": unix_time(),
            "Status": "CREATE_COMPLETE",
            "StatusMessage": "Dataset created successfully",
            "StatusMessageCode": "SUCCESS",
            "DatasetStats": {
                "LabeledEntries": 0,
                "TotalEntries": 0,
                "TotalLabels": 0,
                "ErrorEntries": 0,
            },
            "entries": [],  # internal: list of entry dicts
            "labels": [],  # internal: list of label names
        }
        self._datasets[dataset_arn] = dataset
        # Track on the project
        project.setdefault("Datasets", []).append(
            {"DatasetArn": dataset_arn, "DatasetType": dataset_type}
        )
        return {"DatasetArn": dataset_arn}

    def describe_dataset(self, dataset_arn: str) -> dict[str, Any]:
        if dataset_arn not in self._datasets:
            raise ResourceNotFoundException(
                f"The dataset with ARN {dataset_arn} does not exist"
            )
        ds = self._datasets[dataset_arn]
        return {
            "DatasetDescription": {
                "CreationTimestamp": ds["CreationTimestamp"],
                "LastUpdatedTimestamp": ds["LastUpdatedTimestamp"],
                "Status": ds["Status"],
                "StatusMessage": ds["StatusMessage"],
                "StatusMessageCode": ds.get("StatusMessageCode", "SUCCESS"),
                "DatasetStats": ds["DatasetStats"],
            }
        }

    def delete_dataset(self, dataset_arn: str) -> dict[str, Any]:
        if dataset_arn not in self._datasets:
            raise ResourceNotFoundException(
                f"The dataset with ARN {dataset_arn} does not exist"
            )
        ds = self._datasets[dataset_arn]
        # Remove from project's dataset list
        project_arn = ds["ProjectArn"]
        if project_arn in self._projects:
            project = self._projects[project_arn]
            project["Datasets"] = [
                d for d in project.get("Datasets", []) if d["DatasetArn"] != dataset_arn
            ]
        del self._datasets[dataset_arn]
        return {}

    def list_dataset_entries(
        self,
        dataset_arn: str,
        contains_labels: Optional[list[str]] = None,
        labeled: Optional[bool] = None,
        source_ref_contains: Optional[str] = None,
        has_errors: Optional[bool] = None,
        max_results: int = 100,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        if dataset_arn not in self._datasets:
            raise ResourceNotFoundException(
                f"The dataset with ARN {dataset_arn} does not exist"
            )
        ds = self._datasets[dataset_arn]
        entries = ds.get("entries", [])
        # Return as JSON lines
        import json

        entry_strings = [json.dumps(e) for e in entries]
        start = int(next_token) if next_token else 0
        end = start + max_results
        page = entry_strings[start:end]
        result: dict[str, Any] = {"DatasetEntries": page}
        if end < len(entry_strings):
            result["NextToken"] = str(end)
        return result

    def list_dataset_labels(
        self,
        dataset_arn: str,
        max_results: int = 100,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        if dataset_arn not in self._datasets:
            raise ResourceNotFoundException(
                f"The dataset with ARN {dataset_arn} does not exist"
            )
        ds = self._datasets[dataset_arn]
        labels = ds.get("labels", [])
        start = int(next_token) if next_token else 0
        end = start + max_results
        page = labels[start:end]
        label_descriptions = [{"LabelName": lbl} for lbl in page]
        result: dict[str, Any] = {"DatasetLabelDescriptions": label_descriptions}
        if end < len(labels):
            result["NextToken"] = str(end)
        return result

    # ---- Stream Processors ----

    def create_stream_processor(
        self,
        name: str,
        input_config: dict[str, Any],
        output_config: dict[str, Any],
        role_arn: str,
        settings: dict[str, Any],
        data_sharing_preference: Optional[dict[str, Any]] = None,
        regions_of_interest: Optional[list[dict[str, Any]]] = None,
        notification_channel: Optional[dict[str, Any]] = None,
        kms_key_id: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        if name in self._stream_processors:
            raise ResourceAlreadyExistsException(
                f"A stream processor with name {name} already exists"
            )
        arn = self._stream_processor_arn(name)
        processor = {
            "StreamProcessorArn": arn,
            "Name": name,
            "Input": input_config,
            "Output": output_config,
            "RoleArn": role_arn,
            "Settings": settings,
            "Status": "STOPPED",
            "CreationTimestamp": unix_time(),
            "LastUpdateTimestamp": unix_time(),
            "StatusMessage": "",
            "DataSharingPreference": data_sharing_preference or {"OptIn": False},
            "RegionsOfInterest": regions_of_interest or [],
            "NotificationChannel": notification_channel,
            "KmsKeyId": kms_key_id,
            "Tags": tags or {},
        }
        self._stream_processors[name] = processor
        return {"StreamProcessorArn": arn}

    def describe_stream_processor(self, name: str) -> dict[str, Any]:
        if name not in self._stream_processors:
            raise ResourceNotFoundException(
                f"The stream processor with name {name} does not exist"
            )
        sp = self._stream_processors[name]
        return {
            "Name": sp["Name"],
            "StreamProcessorArn": sp["StreamProcessorArn"],
            "Status": sp["Status"],
            "StatusMessage": sp.get("StatusMessage", ""),
            "CreationTimestamp": sp["CreationTimestamp"],
            "LastUpdateTimestamp": sp["LastUpdateTimestamp"],
            "Input": sp["Input"],
            "Output": sp["Output"],
            "RoleArn": sp["RoleArn"],
            "Settings": sp["Settings"],
            "DataSharingPreference": sp.get("DataSharingPreference", {}),
            "RegionsOfInterest": sp.get("RegionsOfInterest", []),
            "NotificationChannel": sp.get("NotificationChannel"),
            "KmsKeyId": sp.get("KmsKeyId"),
        }

    def delete_stream_processor(self, name: str) -> dict[str, Any]:
        if name not in self._stream_processors:
            raise ResourceNotFoundException(
                f"The stream processor with name {name} does not exist"
            )
        del self._stream_processors[name]
        return {}

    def list_stream_processors(
        self,
        max_results: int = 100,
        next_token: Optional[str] = None,
    ) -> dict[str, Any]:
        all_names = sorted(self._stream_processors.keys())
        start = 0
        if next_token:
            try:
                start = all_names.index(next_token)
            except ValueError:
                start = 0
        end = start + max_results
        page = all_names[start:end]
        processors = []
        for n in page:
            sp = self._stream_processors[n]
            processors.append(
                {
                    "Name": sp["Name"],
                    "Status": sp["Status"],
                }
            )
        result: dict[str, Any] = {"StreamProcessors": processors}
        if end < len(all_names):
            result["NextToken"] = all_names[end]
        return result

    def start_stream_processor(
        self,
        name: str,
        start_selector: Optional[dict[str, Any]] = None,
        stop_selector: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        if name not in self._stream_processors:
            raise ResourceNotFoundException(
                f"The stream processor with name {name} does not exist"
            )
        sp = self._stream_processors[name]
        if sp["Status"] == "RUNNING":
            raise ResourceInUseException(
                f"The stream processor {name} is already running"
            )
        sp["Status"] = "RUNNING"
        sp["LastUpdateTimestamp"] = unix_time()
        result: dict[str, Any] = {"Status": "STARTING"}
        if start_selector:
            result["SessionId"] = _random_uuid()
        return result

    def stop_stream_processor(self, name: str) -> dict[str, Any]:
        if name not in self._stream_processors:
            raise ResourceNotFoundException(
                f"The stream processor with name {name} does not exist"
            )
        sp = self._stream_processors[name]
        sp["Status"] = "STOPPED"
        sp["LastUpdateTimestamp"] = unix_time()
        return {"Status": "STOPPING"}

    def update_stream_processor(
        self,
        name: str,
        settings_for_update: Optional[dict[str, Any]] = None,
        regions_of_interest_for_update: Optional[list[dict[str, Any]]] = None,
        data_sharing_preference_for_update: Optional[dict[str, Any]] = None,
        parameters_to_delete: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        if name not in self._stream_processors:
            raise ResourceNotFoundException(
                f"The stream processor with name {name} does not exist"
            )
        sp = self._stream_processors[name]
        if settings_for_update:
            sp["Settings"].update(settings_for_update)
        if regions_of_interest_for_update is not None:
            sp["RegionsOfInterest"] = regions_of_interest_for_update
        if data_sharing_preference_for_update is not None:
            sp["DataSharingPreference"] = data_sharing_preference_for_update
        if parameters_to_delete:
            for param in parameters_to_delete:
                sp.pop(param, None)
        sp["LastUpdateTimestamp"] = unix_time()
        return {"StreamProcessorArn": sp["StreamProcessorArn"]}

    # ---- Existing operations (preserved) ----

    def start_face_search(self) -> str:
        return self._job_id()

    def start_text_detection(self) -> str:
        return self._job_id()

    def get_face_search(
        self,
    ) -> tuple[str, str, dict[str, Any], list[dict[str, Any]], str, str]:
        """
        This returns hardcoded values and none of the parameters are taken into account.
        """
        return (
            self._job_status(),
            self._status_message(),
            self._video_metadata(),
            self._persons(),
            self._next_token(),
            self._text_model_version(),
        )

    def get_text_detection(
        self,
    ) -> tuple[str, str, dict[str, Any], list[dict[str, Any]], str, str]:
        """
        This returns hardcoded values and none of the parameters are taken into account.
        """
        return (
            self._job_status(),
            self._status_message(),
            self._video_metadata(),
            self._text_detections(),
            self._next_token(),
            self._text_model_version(),
        )

    def compare_faces(
        self,
    ) -> tuple[
        list[dict[str, Any]],
        str,
        str,
        list[dict[str, Any]],
        dict[str, Any],
    ]:
        return (
            self._face_matches(),
            "ROTATE_90",
            "ROTATE_90",
            self._unmatched_faces(),
            self.source_image_face(),
        )

    def detect_labels(self) -> tuple[list[dict[str, Any]], dict[str, Any], str]:
        return (
            self._mobile_phone_label(),
            self._image_properties(),
            "3.0",
        )

    def detect_text(self) -> tuple[list[dict[str, Any]], str]:
        return (
            self._detect_text_text_detections(),
            "3.0",
        )

    def detect_custom_labels(self) -> tuple[list[dict[str, Any]]]:
        return (self._detect_custom_labels_detections(),)

    # private

    def _job_id(self) -> str:
        return _random_id(64)

    def _job_status(self) -> str:
        return "SUCCEEDED"

    def _next_token(self) -> str:
        return ""

    def _status_message(self) -> str:
        return ""

    def _text_model_version(self) -> str:
        return "3.1"

    def _video_metadata(self) -> dict[str, Any]:
        return {
            "Codec": "h264",
            "DurationMillis": 15020,
            "Format": "QuickTime / MOV",
            "FrameRate": 24.0,
            "FrameHeight": 720,
            "FrameWidth": 1280,
            "ColorRange": "LIMITED",
        }

    def _persons(self) -> list[dict[str, Any]]:
        return [
            {
                "Timestamp": 0,
                "Person": {
                    "Index": 0,
                    "Face": {
                        "BoundingBox": {
                            "Width": 0.42217350006103516,
                            "Height": 0.9352386593818665,
                            "Left": 0.31870967149734497,
                            "Top": -0.0049947104416787624,
                        },
                        "Landmarks": [
                            {
                                "Type": "eyeLeft",
                                "X": 0.4800040125846863,
                                "Y": 0.23425640165805817,
                            },
                            {
                                "Type": "eyeRight",
                                "X": 0.63795405626297,
                                "Y": 0.19219470024108887,
                            },
                            {
                                "Type": "mouthLeft",
                                "X": 0.5283276438713074,
                                "Y": 0.6190487146377563,
                            },
                            {
                                "Type": "mouthRight",
                                "X": 0.660395085811615,
                                "Y": 0.5830448269844055,
                            },
                            {
                                "Type": "nose",
                                "X": 0.619724690914154,
                                "Y": 0.3800361752510071,
                            },
                        ],
                        "Pose": {
                            "Roll": -5.063229084014893,
                            "Yaw": 18.038856506347656,
                            "Pitch": 12.567241668701172,
                        },
                        "Quality": {
                            "Brightness": 83.42264556884766,
                            "Sharpness": 67.22731018066406,
                        },
                        "Confidence": 99.99860382080078,
                    },
                },
                "FaceMatches": [
                    {
                        "Similarity": 99.99994659423828,
                        "Face": {
                            "FaceId": "f2489050-020e-4c14-8693-63339847a59d",
                            "BoundingBox": {
                                "Width": 0.7136539816856384,
                                "Height": 0.9471719861030579,
                                "Left": 0.19036999344825745,
                                "Top": -0.012074699625372887,
                            },
                            "ImageId": "f3b180d3-f5ad-39c1-b825-ba30b170a90d",
                            "ExternalImageId": "Dave_Bloggs",
                            "Confidence": 99.99970245361328,
                        },
                    },
                    {
                        "Similarity": 99.9986572265625,
                        "Face": {
                            "FaceId": "f0d22a6a-3436-4d23-ae5b-c5cb2e795581",
                            "BoundingBox": {
                                "Width": 0.7198730111122131,
                                "Height": 1.003640055656433,
                                "Left": 0.1844159960746765,
                                "Top": -0.00142729002982378,
                            },
                            "ImageId": "738d14f3-26be-3066-b1a9-7f4f6bb3ffc6",
                            "ExternalImageId": "Dave_Bloggs",
                            "Confidence": 99.99939727783203,
                        },
                    },
                    {
                        "Similarity": 99.99791717529297,
                        "Face": {
                            "FaceId": "c48162bd-a16a-4e04-ad3c-967761895295",
                            "BoundingBox": {
                                "Width": 0.7364680171012878,
                                "Height": 1.0104399919509888,
                                "Left": 0.1361449956893921,
                                "Top": -0.009593159891664982,
                            },
                            "ImageId": "eae3565c-741b-342c-8e73-379a09ae5346",
                            "ExternalImageId": "Dave_Bloggs",
                            "Confidence": 99.99949645996094,
                        },
                    },
                    {
                        "Similarity": 99.37212371826172,
                        "Face": {
                            "FaceId": "651314bb-28d4-405d-9b13-c32e9ff28299",
                            "BoundingBox": {
                                "Width": 0.3711090087890625,
                                "Height": 0.3609749972820282,
                                "Left": 0.2571589946746826,
                                "Top": 0.21493400633335114,
                            },
                            "ImageId": "068700f5-0b2e-39c0-874b-2c58fa10d833",
                            "ExternalImageId": "Dave_Bloggs",
                            "Confidence": 99.99300384521484,
                        },
                    },
                ],
            }
        ]

    def _text_detections(self) -> list[dict[str, Any]]:
        return [
            {
                "Timestamp": 0,
                "TextDetection": {
                    "DetectedText": "Hello world",
                    "Type": "LINE",
                    "Id": 0,
                    "Confidence": 97.89398956298828,
                    "Geometry": {
                        "BoundingBox": {
                            "Width": 0.1364741027355194,
                            "Height": 0.0318513885140419,
                            "Left": 0.4310702085494995,
                            "Top": 0.876121461391449,
                        },
                        "Polygon": [
                            {"X": 0.4310702085494995, "Y": 0.8769540190696716},
                            {"X": 0.5673548579216003, "Y": 0.876121461391449},
                            {"X": 0.5675443410873413, "Y": 0.90714031457901},
                            {"X": 0.4312596917152405, "Y": 0.9079728722572327},
                        ],
                    },
                },
            },
            {
                "Timestamp": 0,
                "TextDetection": {
                    "DetectedText": "Hello",
                    "Type": "WORD",
                    "Id": 1,
                    "ParentId": 0,
                    "Confidence": 99.1568832397461,
                    "Geometry": {
                        "BoundingBox": {
                            "Width": 0.0648193359375,
                            "Height": 0.0234375,
                            "Left": 0.43121337890625,
                            "Top": 0.876953125,
                        },
                        "Polygon": [
                            {"X": 0.43121337890625, "Y": 0.876953125},
                            {"X": 0.49603271484375, "Y": 0.876953125},
                            {"X": 0.49603271484375, "Y": 0.900390625},
                            {"X": 0.43121337890625, "Y": 0.900390625},
                        ],
                    },
                },
            },
            {
                "Timestamp": 0,
                "TextDetection": {
                    "DetectedText": "world",
                    "Type": "WORD",
                    "Id": 2,
                    "ParentId": 0,
                    "Confidence": 96.63108825683594,
                    "Geometry": {
                        "BoundingBox": {
                            "Width": 0.07103776931762695,
                            "Height": 0.02804870530962944,
                            "Left": 0.4965003430843353,
                            "Top": 0.8795245885848999,
                        },
                        "Polygon": [
                            {"X": 0.4965003430843353, "Y": 0.8809727430343628},
                            {"X": 0.5673661231994629, "Y": 0.8795245885848999},
                            {"X": 0.5675381422042847, "Y": 0.9061251282691956},
                            {"X": 0.4966723322868347, "Y": 0.9075732827186584},
                        ],
                    },
                },
            },
            {
                "Timestamp": 1000,
                "TextDetection": {
                    "DetectedText": "Goodbye world",
                    "Type": "LINE",
                    "Id": 0,
                    "Confidence": 98.9729995727539,
                    "Geometry": {
                        "BoundingBox": {
                            "Width": 0.13677978515625,
                            "Height": 0.0302734375,
                            "Left": 0.43121337890625,
                            "Top": 0.876953125,
                        },
                        "Polygon": [
                            {"X": 0.43121337890625, "Y": 0.876953125},
                            {"X": 0.5679931640625, "Y": 0.876953125},
                            {"X": 0.5679931640625, "Y": 0.9072265625},
                            {"X": 0.43121337890625, "Y": 0.9072265625},
                        ],
                    },
                },
            },
            {
                "Timestamp": 1000,
                "TextDetection": {
                    "DetectedText": "Goodbye",
                    "Type": "WORD",
                    "Id": 1,
                    "ParentId": 0,
                    "Confidence": 99.7258529663086,
                    "Geometry": {
                        "BoundingBox": {
                            "Width": 0.0648193359375,
                            "Height": 0.0234375,
                            "Left": 0.43121337890625,
                            "Top": 0.876953125,
                        },
                        "Polygon": [
                            {"X": 0.43121337890625, "Y": 0.876953125},
                            {"X": 0.49603271484375, "Y": 0.876953125},
                            {"X": 0.49603271484375, "Y": 0.900390625},
                            {"X": 0.43121337890625, "Y": 0.900390625},
                        ],
                    },
                },
            },
            {
                "Timestamp": 1000,
                "TextDetection": {
                    "DetectedText": "world",
                    "Type": "WORD",
                    "Id": 2,
                    "ParentId": 0,
                    "Confidence": 98.22015380859375,
                    "Geometry": {
                        "BoundingBox": {
                            "Width": 0.0703125,
                            "Height": 0.0263671875,
                            "Left": 0.4976806640625,
                            "Top": 0.880859375,
                        },
                        "Polygon": [
                            {"X": 0.4976806640625, "Y": 0.880859375},
                            {"X": 0.5679931640625, "Y": 0.880859375},
                            {"X": 0.5679931640625, "Y": 0.9072265625},
                            {"X": 0.4976806640625, "Y": 0.9072265625},
                        ],
                    },
                },
            },
        ]

    def _face_matches(self) -> list[dict[str, Any]]:
        return [
            {
                "Face": {
                    "BoundingBox": {
                        "Width": 0.5521978139877319,
                        "Top": 0.1203877404332161,
                        "Left": 0.23626373708248138,
                        "Height": 0.3126954436302185,
                    },
                    "Confidence": 99.98751068115234,
                    "Pose": {
                        "Yaw": -82.36799621582031,
                        "Roll": -62.13221740722656,
                        "Pitch": 0.8652129173278809,
                    },
                    "Quality": {
                        "Sharpness": 99.99880981445312,
                        "Brightness": 54.49755096435547,
                    },
                    "Landmarks": [
                        {
                            "Y": 0.2996366024017334,
                            "X": 0.41685718297958374,
                            "Type": "eyeLeft",
                        },
                        {
                            "Y": 0.2658946216106415,
                            "X": 0.4414493441581726,
                            "Type": "eyeRight",
                        },
                        {
                            "Y": 0.3465650677680969,
                            "X": 0.48636093735694885,
                            "Type": "nose",
                        },
                        {
                            "Y": 0.30935320258140564,
                            "X": 0.6251809000968933,
                            "Type": "mouthLeft",
                        },
                        {
                            "Y": 0.26942989230155945,
                            "X": 0.6454493403434753,
                            "Type": "mouthRight",
                        },
                    ],
                },
                "Similarity": 100.0,
            }
        ]

    def _unmatched_faces(self) -> list[dict[str, Any]]:
        return [
            {
                "BoundingBox": {
                    "Width": 0.4890109896659851,
                    "Top": 0.6566604375839233,
                    "Left": 0.10989011079072952,
                    "Height": 0.278298944234848,
                },
                "Confidence": 99.99992370605469,
                "Pose": {
                    "Yaw": 51.51519012451172,
                    "Roll": -110.32493591308594,
                    "Pitch": -2.322134017944336,
                },
                "Quality": {
                    "Sharpness": 99.99671173095703,
                    "Brightness": 57.23163986206055,
                },
                "Landmarks": [
                    {
                        "Y": 0.8288310766220093,
                        "X": 0.3133862614631653,
                        "Type": "eyeLeft",
                    },
                    {
                        "Y": 0.7632885575294495,
                        "X": 0.28091415762901306,
                        "Type": "eyeRight",
                    },
                    {"Y": 0.7417283654212952, "X": 0.3631140887737274, "Type": "nose"},
                    {
                        "Y": 0.8081989884376526,
                        "X": 0.48565614223480225,
                        "Type": "mouthLeft",
                    },
                    {
                        "Y": 0.7548204660415649,
                        "X": 0.46090251207351685,
                        "Type": "mouthRight",
                    },
                ],
            }
        ]

    def source_image_face(self) -> dict[str, Any]:
        return {
            "BoundingBox": {
                "Width": 0.5521978139877319,
                "Top": 0.1203877404332161,
                "Left": 0.23626373708248138,
                "Height": 0.3126954436302185,
            },
            "Confidence": 99.98751068115234,
        }

    def _mobile_phone_label(self) -> list[dict[str, Any]]:
        return [
            {
                "Name": "Mobile Phone",
                "Parents": [{"Name": "Phone"}],
                "Aliases": [{"Name": "Cell Phone"}],
                "Categories": [{"Name": "Technology and Computing"}],
                "Confidence": 99.9364013671875,
                "Instances": [
                    {
                        "BoundingBox": {
                            "Width": 0.26779675483703613,
                            "Height": 0.8562285900115967,
                            "Left": 0.3604024350643158,
                            "Top": 0.09245597571134567,
                        },
                        "Confidence": 99.9364013671875,
                        "DominantColors": [
                            {
                                "Red": 120,
                                "Green": 137,
                                "Blue": 132,
                                "HexCode": "3A7432",
                                "SimplifiedColor": "red",
                                "CssColor": "fuscia",
                                "PixelPercentage": 40.10,
                            }
                        ],
                    }
                ],
            }
        ]

    def _image_properties(self) -> dict[str, Any]:
        return {
            "ImageProperties": {
                "Quality": {
                    "Brightness": 40,
                    "Sharpness": 40,
                    "Contrast": 24,
                },
                "DominantColors": [
                    {
                        "Red": 120,
                        "Green": 137,
                        "Blue": 132,
                        "HexCode": "3A7432",
                        "SimplifiedColor": "red",
                        "CssColor": "fuscia",
                        "PixelPercentage": 40.10,
                    }
                ],
                "Foreground": {
                    "Quality": {
                        "Brightness": 40,
                        "Sharpness": 40,
                    },
                    "DominantColors": [
                        {
                            "Red": 200,
                            "Green": 137,
                            "Blue": 132,
                            "HexCode": "3A7432",
                            "CSSColor": "",
                            "SimplifiedColor": "red",
                            "PixelPercentage": 30.70,
                        }
                    ],
                },
                "Background": {
                    "Quality": {
                        "Brightness": 40,
                        "Sharpness": 40,
                    },
                    "DominantColors": [
                        {
                            "Red": 200,
                            "Green": 137,
                            "Blue": 132,
                            "HexCode": "3A7432",
                            "CSSColor": "",
                            "SimplifiedColor": "Red",
                            "PixelPercentage": 10.20,
                        }
                    ],
                },
            }
        }

    def _detect_text_text_detections(self) -> list[dict[str, Any]]:
        return [
            {
                "Confidence": 99.35693359375,
                "DetectedText": "IT'S",
                "Geometry": {
                    "BoundingBox": {
                        "Height": 0.09988046437501907,
                        "Left": 0.6684935688972473,
                        "Top": 0.18226495385169983,
                        "Width": 0.1461552083492279,
                    },
                    "Polygon": [
                        {"X": 0.6684935688972473, "Y": 0.1838926374912262},
                        {"X": 0.8141663074493408, "Y": 0.18226495385169983},
                        {"X": 0.8146487474441528, "Y": 0.28051772713661194},
                        {"X": 0.6689760088920593, "Y": 0.2821454107761383},
                    ],
                },
                "Id": 0,
                "Type": "LINE",
            },
            {
                "Confidence": 99.6207275390625,
                "DetectedText": "MONDAY",
                "Geometry": {
                    "BoundingBox": {
                        "Height": 0.11442459374666214,
                        "Left": 0.5566731691360474,
                        "Top": 0.3525116443634033,
                        "Width": 0.39574965834617615,
                    },
                    "Polygon": [
                        {"X": 0.5566731691360474, "Y": 0.353712260723114},
                        {"X": 0.9522717595100403, "Y": 0.3525116443634033},
                        {"X": 0.9524227976799011, "Y": 0.4657355844974518},
                        {"X": 0.5568241477012634, "Y": 0.46693623065948486},
                    ],
                },
                "Id": 1,
                "Type": "LINE",
            },
            {
                "Confidence": 99.6160888671875,
                "DetectedText": "but keep",
                "Geometry": {
                    "BoundingBox": {
                        "Height": 0.08314694464206696,
                        "Left": 0.6398131847381592,
                        "Top": 0.5267938375473022,
                        "Width": 0.2021435648202896,
                    },
                    "Polygon": [
                        {"X": 0.640289306640625, "Y": 0.5267938375473022},
                        {"X": 0.8419567942619324, "Y": 0.5295097827911377},
                        {"X": 0.8414806723594666, "Y": 0.609940767288208},
                        {"X": 0.6398131847381592, "Y": 0.6072247624397278},
                    ],
                },
                "Id": 2,
                "Type": "LINE",
            },
            {
                "Confidence": 88.95134735107422,
                "DetectedText": "Smiling",
                "Geometry": {
                    "BoundingBox": {
                        "Height": 0.4326171875,
                        "Left": 0.46289217472076416,
                        "Top": 0.5634765625,
                        "Width": 0.5371078252792358,
                    },
                    "Polygon": [
                        {"X": 0.46289217472076416, "Y": 0.5634765625},
                        {"X": 1.0, "Y": 0.5634765625},
                        {"X": 1.0, "Y": 0.99609375},
                        {"X": 0.46289217472076416, "Y": 0.99609375},
                    ],
                },
                "Id": 3,
                "Type": "LINE",
            },
            {
                "Confidence": 99.35693359375,
                "DetectedText": "IT'S",
                "Geometry": {
                    "BoundingBox": {
                        "Height": 0.09988046437501907,
                        "Left": 0.6684935688972473,
                        "Top": 0.18226495385169983,
                        "Width": 0.1461552083492279,
                    },
                    "Polygon": [
                        {"X": 0.6684935688972473, "Y": 0.1838926374912262},
                        {"X": 0.8141663074493408, "Y": 0.18226495385169983},
                        {"X": 0.8146487474441528, "Y": 0.28051772713661194},
                        {"X": 0.6689760088920593, "Y": 0.2821454107761383},
                    ],
                },
                "Id": 4,
                "ParentId": 0,
                "Type": "WORD",
            },
            {
                "Confidence": 99.6207275390625,
                "DetectedText": "MONDAY",
                "Geometry": {
                    "BoundingBox": {
                        "Height": 0.11442466825246811,
                        "Left": 0.5566731691360474,
                        "Top": 0.35251158475875854,
                        "Width": 0.39574965834617615,
                    },
                    "Polygon": [
                        {"X": 0.5566731691360474, "Y": 0.3537122905254364},
                        {"X": 0.9522718787193298, "Y": 0.35251158475875854},
                        {"X": 0.9524227976799011, "Y": 0.4657355546951294},
                        {"X": 0.5568241477012634, "Y": 0.46693626046180725},
                    ],
                },
                "Id": 5,
                "ParentId": 1,
                "Type": "WORD",
            },
            {
                "Confidence": 99.96778869628906,
                "DetectedText": "but",
                "Geometry": {
                    "BoundingBox": {
                        "Height": 0.0625,
                        "Left": 0.6402802467346191,
                        "Top": 0.5283203125,
                        "Width": 0.08027780801057816,
                    },
                    "Polygon": [
                        {"X": 0.6402802467346191, "Y": 0.5283203125},
                        {"X": 0.7205580472946167, "Y": 0.5283203125},
                        {"X": 0.7205580472946167, "Y": 0.5908203125},
                        {"X": 0.6402802467346191, "Y": 0.5908203125},
                    ],
                },
                "Id": 6,
                "ParentId": 2,
                "Type": "WORD",
            },
            {
                "Confidence": 99.26438903808594,
                "DetectedText": "keep",
                "Geometry": {
                    "BoundingBox": {
                        "Height": 0.0818721204996109,
                        "Left": 0.7344760298728943,
                        "Top": 0.5280686020851135,
                        "Width": 0.10748066753149033,
                    },
                    "Polygon": [
                        {"X": 0.7349520921707153, "Y": 0.5280686020851135},
                        {"X": 0.8419566750526428, "Y": 0.5295097827911377},
                        {"X": 0.8414806127548218, "Y": 0.6099407076835632},
                        {"X": 0.7344760298728943, "Y": 0.6084995269775391},
                    ],
                },
                "Id": 7,
                "ParentId": 2,
                "Type": "WORD",
            },
            {
                "Confidence": 88.95134735107422,
                "DetectedText": "Smiling",
                "Geometry": {
                    "BoundingBox": {
                        "Height": 0.4326171875,
                        "Left": 0.46289217472076416,
                        "Top": 0.5634765625,
                        "Width": 0.5371078252792358,
                    },
                    "Polygon": [
                        {"X": 0.46289217472076416, "Y": 0.5634765625},
                        {"X": 1.0, "Y": 0.5634765625},
                        {"X": 1.0, "Y": 0.99609375},
                        {"X": 0.46289217472076416, "Y": 0.99609375},
                    ],
                },
                "Id": 8,
                "ParentId": 3,
                "Type": "WORD",
            },
        ]

    def _detect_custom_labels_detections(self) -> list[dict[str, Any]]:
        return [
            {
                "Name": "MyLogo",
                "Confidence": 77.7729721069336,
                "Geometry": {
                    "BoundingBox": {
                        "Width": 0.198987677693367,
                        "Height": 0.31296101212501526,
                        "Left": 0.07924537360668182,
                        "Top": 0.4037395715713501,
                    }
                },
            }
        ]


rekognition_backends = BackendDict(RekognitionBackend, "rekognition")
