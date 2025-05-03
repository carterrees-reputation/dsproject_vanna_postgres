    CREATE TABLE reviews (
        comment_id INT PRIMARY KEY,
        tenant_id INT,
        location_id INT,
        comment TEXT,
        created_date TIMESTAMP WITHOUT TIME ZONE
    );