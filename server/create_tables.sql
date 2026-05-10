-- SmartMarket Database Schema
-- Run this on your Azure SQL Database before starting the server

CREATE TABLE dbo.readProduct (
    product_id                 NVARCHAR(50)   NOT NULL PRIMARY KEY,
    name                       NVARCHAR(255)  NULL,
    current_price              FLOAT          NULL,
    cost_price                 FLOAT          NULL,
    quantity                   INT            NULL,
    brand                      NVARCHAR(100)  NULL,
    category                   NVARCHAR(100)  NULL,
    is_on_promotion            BIT            NOT NULL DEFAULT 0,
    promotion_discount_percent FLOAT          NULL DEFAULT 0.0,
    image_url                  NVARCHAR(500)  NULL,
    note                       NVARCHAR(MAX)  NULL,
    inventory_value            FLOAT          NULL,
    total_profit               FLOAT          NULL DEFAULT 0.0,
    updated_at_utc             DATETIME2      NULL
);

CREATE TABLE dbo.Events (
    event_id                   INT            IDENTITY(1,1) PRIMARY KEY,
    product_id                 NVARCHAR(50)   NOT NULL,
    event_type                 NVARCHAR(50)   NOT NULL,
    occurred_at_utc            DATETIME2      NOT NULL,
    name                       NVARCHAR(255)  NULL,
    current_price              FLOAT          NULL,
    cost_price                 FLOAT          NULL,
    quantity_after             INT            NULL,
    quantity_delta             INT            NULL,
    brand                      NVARCHAR(100)  NULL,
    category                   NVARCHAR(100)  NULL,
    is_on_promotion            BIT            NULL,
    promotion_discount_percent FLOAT          NULL,
    image_url                  NVARCHAR(500)  NULL,
    note                       NVARCHAR(MAX)  NULL,
    sale_unit_price            FLOAT          NULL,
    sale_unit_cost             FLOAT          NULL,
    purchase_unit_cost         FLOAT          NULL
);
