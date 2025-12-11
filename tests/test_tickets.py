from fastapi import status
from fastapi.testclient import TestClient


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health check returns ok status."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}


class TestCreateTicket:
    """Tests for POST /tickets/ endpoint."""

    def test_create_ticket_success(self, client: TestClient) -> None:
        """Test creating a ticket with valid data."""
        ticket_data = {
            "title": "Test Ticket",
            "description": "This is a test ticket",
        }
        response = client.post("/tickets/", json=ticket_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == ticket_data["title"]
        assert data["description"] == ticket_data["description"]
        assert data["status"] == "open"
        assert "id" in data
        assert "created_at" in data

    def test_create_ticket_with_status(self, client: TestClient) -> None:
        """Test creating a ticket with explicit status."""
        ticket_data = {
            "title": "Stalled Ticket",
            "description": "This ticket is stalled",
            "status": "stalled",
        }
        response = client.post("/tickets/", json=ticket_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["status"] == "stalled"

    def test_create_ticket_missing_title(self, client: TestClient) -> None:
        """Test creating a ticket without title fails."""
        ticket_data = {"description": "Missing title"}
        response = client.post("/tickets/", json=ticket_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_ticket_missing_description(self, client: TestClient) -> None:
        """Test creating a ticket without description fails."""
        ticket_data = {"title": "Missing description"}
        response = client.post("/tickets/", json=ticket_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_ticket_empty_title(self, client: TestClient) -> None:
        """Test creating a ticket with empty title fails."""
        ticket_data = {"title": "", "description": "Valid description"}
        response = client.post("/tickets/", json=ticket_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_ticket_invalid_status(self, client: TestClient) -> None:
        """Test creating a ticket with invalid status fails."""
        ticket_data = {
            "title": "Test",
            "description": "Test",
            "status": "invalid_status",
        }
        response = client.post("/tickets/", json=ticket_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestListTickets:
    """Tests for GET /tickets/ endpoint."""

    def test_list_tickets_empty(self, client: TestClient) -> None:
        """Test listing tickets when none exist."""
        response = client.get("/tickets/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_tickets_multiple(self, client: TestClient) -> None:
        """Test listing multiple tickets."""
        # Create tickets
        for i in range(3):
            client.post(
                "/tickets/",
                json={"title": f"Ticket {i}", "description": f"Description {i}"},
            )

        response = client.get("/tickets/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_list_tickets_pagination(self, client: TestClient) -> None:
        """Test listing tickets with pagination."""
        # Create tickets
        for i in range(5):
            client.post(
                "/tickets/",
                json={"title": f"Ticket {i}", "description": f"Description {i}"},
            )

        response = client.get("/tickets/?skip=2&limit=2")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2


class TestGetTicket:
    """Tests for GET /tickets/{ticket_id} endpoint."""

    def test_get_ticket_success(self, client: TestClient) -> None:
        """Test getting an existing ticket."""
        # Create a ticket
        create_response = client.post(
            "/tickets/",
            json={"title": "Test Ticket", "description": "Test Description"},
        )
        ticket_id = create_response.json()["id"]

        response = client.get(f"/tickets/{ticket_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == ticket_id
        assert data["title"] == "Test Ticket"

    def test_get_ticket_not_found(self, client: TestClient) -> None:
        """Test getting a non-existent ticket."""
        response = client.get("/tickets/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()


class TestUpdateTicket:
    """Tests for PUT /tickets/{ticket_id} endpoint."""

    def test_update_ticket_full(self, client: TestClient) -> None:
        """Test updating all fields of a ticket."""
        # Create a ticket
        create_response = client.post(
            "/tickets/",
            json={"title": "Original", "description": "Original description"},
        )
        ticket_id = create_response.json()["id"]

        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "status": "stalled",
        }
        response = client.put(f"/tickets/{ticket_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["status"] == update_data["status"]

    def test_update_ticket_partial(self, client: TestClient) -> None:
        """Test updating only some fields of a ticket."""
        # Create a ticket
        create_response = client.post(
            "/tickets/",
            json={"title": "Original", "description": "Original description"},
        )
        ticket_id = create_response.json()["id"]

        response = client.put(f"/tickets/{ticket_id}", json={"title": "New Title"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "New Title"
        assert data["description"] == "Original description"  # Unchanged

    def test_update_ticket_not_found(self, client: TestClient) -> None:
        """Test updating a non-existent ticket."""
        response = client.put("/tickets/99999", json={"title": "New Title"})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_ticket_cannot_close_via_put(self, client: TestClient) -> None:
        """Test that setting status to closed via PUT is not allowed."""
        # Create a ticket
        create_response = client.post(
            "/tickets/",
            json={"title": "Test", "description": "Test"},
        )
        ticket_id = create_response.json()["id"]

        response = client.put(f"/tickets/{ticket_id}", json={"status": "closed"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "close" in response.json()["detail"].lower()


class TestCloseTicket:
    """Tests for PATCH /tickets/{ticket_id}/close endpoint."""

    def test_close_ticket_success(self, client: TestClient) -> None:
        """Test closing an open ticket."""
        # Create a ticket
        create_response = client.post(
            "/tickets/",
            json={"title": "Test", "description": "Test"},
        )
        ticket_id = create_response.json()["id"]

        response = client.patch(f"/tickets/{ticket_id}/close")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "closed"

    def test_close_ticket_already_closed(self, client: TestClient) -> None:
        """Test closing an already closed ticket fails."""
        # Create and close a ticket
        create_response = client.post(
            "/tickets/",
            json={"title": "Test", "description": "Test"},
        )
        ticket_id = create_response.json()["id"]
        client.patch(f"/tickets/{ticket_id}/close")

        # Try to close again
        response = client.patch(f"/tickets/{ticket_id}/close")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already closed" in response.json()["detail"].lower()

    def test_close_ticket_not_found(self, client: TestClient) -> None:
        """Test closing a non-existent ticket."""
        response = client.patch("/tickets/99999/close")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_close_stalled_ticket(self, client: TestClient) -> None:
        """Test closing a stalled ticket succeeds."""
        # Create a stalled ticket
        create_response = client.post(
            "/tickets/",
            json={"title": "Test", "description": "Test", "status": "stalled"},
        )
        ticket_id = create_response.json()["id"]

        response = client.patch(f"/tickets/{ticket_id}/close")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "closed"
