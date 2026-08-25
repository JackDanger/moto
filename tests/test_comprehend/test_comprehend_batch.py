import boto3

from moto import mock_aws


@mock_aws
def test_batch_detect_dominant_language():
    client = boto3.client("comprehend", region_name="us-east-1")
    resp = client.batch_detect_dominant_language(TextList=["Hello world", "Bonjour"])
    assert len(resp["ResultList"]) == 2
    assert resp["ResultList"][0]["Index"] == 0
    assert resp["ResultList"][0]["Languages"][0]["LanguageCode"] == "en"
    assert resp["ResultList"][1]["Index"] == 1
    assert resp["ErrorList"] == []


@mock_aws
def test_batch_detect_entities():
    client = boto3.client("comprehend", region_name="us-east-1")
    resp = client.batch_detect_entities(
        TextList=["John lives in Seattle", "It is raining"],
        LanguageCode="en",
    )
    assert len(resp["ResultList"]) == 2
    assert resp["ResultList"][0]["Index"] == 0
    assert "Entities" in resp["ResultList"][0]
    assert resp["ResultList"][1]["Index"] == 1
    assert resp["ErrorList"] == []


@mock_aws
def test_batch_detect_key_phrases():
    client = boto3.client("comprehend", region_name="us-east-1")
    resp = client.batch_detect_key_phrases(
        TextList=["The quick brown fox", "A sunny day"],
        LanguageCode="en",
    )
    assert len(resp["ResultList"]) == 2
    assert resp["ResultList"][0]["Index"] == 0
    assert "KeyPhrases" in resp["ResultList"][0]
    assert resp["ErrorList"] == []


@mock_aws
def test_batch_detect_sentiment():
    client = boto3.client("comprehend", region_name="us-east-1")
    resp = client.batch_detect_sentiment(
        TextList=["I love this", "This is terrible"],
        LanguageCode="en",
    )
    assert len(resp["ResultList"]) == 2
    assert resp["ResultList"][0]["Index"] == 0
    assert resp["ResultList"][0]["Sentiment"] == "NEUTRAL"
    assert "SentimentScore" in resp["ResultList"][0]
    assert resp["ErrorList"] == []


@mock_aws
def test_batch_detect_syntax():
    client = boto3.client("comprehend", region_name="us-east-1")
    resp = client.batch_detect_syntax(
        TextList=["It is raining", "The sun is shining"],
        LanguageCode="en",
    )
    assert len(resp["ResultList"]) == 2
    assert resp["ResultList"][0]["Index"] == 0
    assert "SyntaxTokens" in resp["ResultList"][0]
    assert resp["ErrorList"] == []


@mock_aws
def test_batch_detect_targeted_sentiment():
    client = boto3.client("comprehend", region_name="us-east-1")
    resp = client.batch_detect_targeted_sentiment(
        TextList=["I love the new phone", "The service was bad"],
        LanguageCode="en",
    )
    assert len(resp["ResultList"]) == 2
    assert resp["ResultList"][0]["Index"] == 0
    assert "Entities" in resp["ResultList"][0]
    assert resp["ErrorList"] == []


@mock_aws
def test_detect_toxic_content():
    client = boto3.client("comprehend", region_name="us-east-1")
    resp = client.detect_toxic_content(
        TextSegments=[
            {"Text": "You are wonderful"},
            {"Text": "Have a nice day"},
        ],
        LanguageCode="en",
    )
    assert len(resp["ResultList"]) == 2
    assert resp["ResultList"][0]["Toxicity"] == 0.01
    labels = resp["ResultList"][0]["Labels"]
    label_names = [l["Name"] for l in labels]
    assert "PROFANITY" in label_names
    assert "HATE_SPEECH" in label_names
    assert all(l["Score"] == 0.01 for l in labels)


@mock_aws
def test_batch_detect_dominant_language_single_item():
    client = boto3.client("comprehend", region_name="us-east-1")
    resp = client.batch_detect_dominant_language(TextList=["Hello"])
    assert len(resp["ResultList"]) == 1
    assert resp["ResultList"][0]["Index"] == 0


@mock_aws
def test_detect_toxic_content_single_segment():
    client = boto3.client("comprehend", region_name="us-east-1")
    resp = client.detect_toxic_content(
        TextSegments=[{"Text": "This is fine"}],
        LanguageCode="en",
    )
    assert len(resp["ResultList"]) == 1
    assert len(resp["ResultList"][0]["Labels"]) == 7
