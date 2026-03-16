import base64
import typing
from dataclasses import dataclass

from google.cloud import aiplatform
from google.protobuf import struct_pb2

# Inspired from https://stackoverflow.com/questions/34269772/type-hints-in-namedtuple.
class EmbeddingResponse(typing.NamedTuple):
    @dataclass
    class VideoEmbedding:
        start_offset_sec: int
        end_offset_sec: int
        embedding: typing.Sequence[float]

    text_embedding: typing.Sequence[float]
    image_embedding: typing.Sequence[float]
    video_embeddings: typing.Sequence[VideoEmbedding]

class EmbeddingPredictionClient:
    """Wrapper around Prediction Service Client."""

    def __init__(self, project: str,
                 location: str = "us-central1",
                 api_regional_endpoint: str = "us-central1-aiplatform.googleapis.com"):
        client_options = {"api_endpoint": api_regional_endpoint}
        # Initialize client that will be used to create and send requests.
        # This client only needs to be created once, and can be reused for multiple requests.
        self.client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
        self.location = location
        self.project = project

    def get_embedding(self, text: str = None, image_bytes: bytes = None, video_uri: str = None,
                      start_offset_sec: int = 0, end_offset_sec: int = 120, interval_sec: int = 16):
        if not text and not image_bytes and not video_uri:
            raise ValueError('At least one of text or image_bytes or video_uri must be specified.')

        instance = struct_pb2.Struct()
        if text:
            instance.fields['text'].string_value = text

        if image_bytes:
            encoded_content = base64.b64encode(image_bytes).decode("utf-8")
            image_struct = instance.fields['image'].struct_value
            image_struct.fields['bytesBase64Encoded'].string_value = encoded_content

        if video_uri:
            video_struct = instance.fields['video'].struct_value
            video_struct.fields['gcsUri'].string_value = video_uri
            video_config_struct = video_struct.fields['videoSegmentConfig'].struct_value
            video_config_struct.fields['startOffsetSec'].number_value = start_offset_sec
            video_config_struct.fields['endOffsetSec'].number_value = end_offset_sec
            video_config_struct.fields['intervalSec'].number_value = interval_sec

        instances = [instance]
        endpoint = (f"projects/{self.project}/locations/{self.location}"
                    "/publishers/google/models/multimodalembedding@001")
        response = self.client.predict(endpoint=endpoint, instances=instances)

        text_embedding = None
        if text:
            text_emb_value = response.predictions[0]['textEmbedding']
            text_embedding = [v for v in text_emb_value]

        image_embedding = None
        if image_bytes:
            image_emb_value = response.predictions[0]['imageEmbedding']
            image_embedding = [v for v in image_emb_value]

        video_embeddings = None
        if video_uri:
            video_emb_values = response.predictions[0]['videoEmbeddings']
            video_embeddings = [
                EmbeddingResponse.VideoEmbedding(start_offset_sec=v['startOffsetSec'], 
                                                 end_offset_sec=v['endOffsetSec'],
                                                 embedding=[x for x in v['embedding']])
                for v in
                video_emb_values]

        return EmbeddingResponse(
            text_embedding=text_embedding,
            image_embedding=image_embedding,
            video_embeddings=video_embeddings)