import io

def test_upload_file(client, s3_mock):
    file_data = b"Test file content"
    response = client.post(
        "/upload/",
        files={"file": ("test.txt", io.BytesIO(file_data), "text/plain")},
    )
    assert response.status_code == 200
    assert "uploaded successfully" in response.json()["message"]