---- added write_time for tracking importing to odoo

----
ALTER TABLE [dbo].[Customer] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [IdxUpdate_Customer] ON [dbo].[Customer] ([write_time])
GO

UPDATE [dbo].[Customer] SET write_time = CURRENT_TIMESTAMP
GO

ALTER TABLE [dbo].[Customer] ADD CONSTRAINT CONSTRAINT_Customer_write_time DEFAULT GETDATE() FOR write_time
GO

CREATE TRIGGER [dbo].[CustomerUpdateTrigger]
ON [dbo].[Customer]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.Customer AS t
            INNER JOIN inserted AS i 
            ON t.ID = i.ID;
    END
END
GO


----
ALTER TABLE [dbo].[PartsIn] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [IdxUpdate_PartsIn] ON [dbo].[PartsIn] ([write_time])
GO

UPDATE [dbo].[PartsIn] SET write_time = CURRENT_TIMESTAMP
GO

ALTER TABLE [dbo].[PartsIn] ADD CONSTRAINT CONSTRAINT_PartsIn_write_time DEFAULT GETDATE() FOR write_time
GO

CREATE TRIGGER [dbo].[PartsInUpdateTrigger]
ON [dbo].[PartsIn]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.PartsIn AS t
            INNER JOIN inserted AS i 
            ON t.ID = i.ID;
    END
END
GO


----
ALTER TABLE [dbo].[PartsInQty] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [IdxUpdate_PartsInQty] ON [dbo].[PartsInQty] ([write_time])
GO

UPDATE [dbo].[PartsInQty] SET write_time = CURRENT_TIMESTAMP
GO

ALTER TABLE [dbo].[PartsInQty] ADD CONSTRAINT CONSTRAINT_PartsInQty_write_time DEFAULT GETDATE() FOR write_time
GO

CREATE TRIGGER [dbo].[PartsInQtyUpdateTrigger]
ON [dbo].[PartsInQty]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.PartsInQty AS t
            INNER JOIN inserted AS i 
            ON t.PID = i.PID;
    END
END
GO


----
ALTER TABLE [dbo].[PartsInQc] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [IdxUpdate_PartsInQc] ON [dbo].[PartsInQc] ([write_time])
GO

UPDATE [dbo].[PartsInQc] SET write_time = CURRENT_TIMESTAMP
GO

ALTER TABLE [dbo].[PartsInQc] ADD CONSTRAINT CONSTRAINT_PartsInQc_write_time DEFAULT GETDATE() FOR write_time
GO

CREATE TRIGGER [dbo].[PartsInQcUpdateTrigger]
ON [dbo].[PartsInQc]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.PartsInQc AS t
            INNER JOIN inserted AS i 
            ON t.PID = i.PID;
    END
END
GO


----
ALTER TABLE [dbo].[PartsOut] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [IdxUpdate_PartsOut] ON [dbo].[PartsOut] ([write_time])
GO

UPDATE [dbo].[PartsOut] SET write_time = CURRENT_TIMESTAMP
GO

ALTER TABLE [dbo].[PartsOut] ADD CONSTRAINT CONSTRAINT_PartsOut_write_time DEFAULT GETDATE() FOR write_time
GO

CREATE TRIGGER [dbo].[PartsOutUpdateTrigger]
ON [dbo].[PartsOut]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.PartsOut AS t
            INNER JOIN inserted AS i 
            ON t.ID = i.ID;
    END
END
GO


----
ALTER TABLE [dbo].[PartsOutQty] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [IdxUpdate_PartsOutQty] ON [dbo].[PartsOutQty] ([write_time])
GO

UPDATE [dbo].[PartsOutQty] SET write_time = CURRENT_TIMESTAMP
GO

ALTER TABLE [dbo].[PartsOutQty] ADD CONSTRAINT CONSTRAINT_PartsOutQty_write_time DEFAULT GETDATE() FOR write_time
GO

CREATE TRIGGER [dbo].[PartsOutQtyUpdateTrigger]
ON [dbo].[PartsOutQty]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.PartsOutQty AS t
            INNER JOIN inserted AS i 
            ON t.PID = i.PID;
    END
END
GO


----
ALTER TABLE [dbo].[Process] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [IdxUpdate_Process] ON [dbo].[Process] ([write_time])
GO

UPDATE [dbo].[Process] SET write_time = CURRENT_TIMESTAMP
GO

ALTER TABLE [dbo].[Process] ADD CONSTRAINT CONSTRAINT_Process_write_time DEFAULT GETDATE() FOR write_time
GO

CREATE TRIGGER [dbo].[ProcessUpdateTrigger]
ON [dbo].[Process]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.Process AS t
            INNER JOIN inserted AS i 
            ON t.ProcessID = i.ProcessID;
    END
END
GO


----
ALTER TABLE [dbo].[Product] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [IdxUpdate_Product] ON [dbo].[Product] ([write_time])
GO

UPDATE [dbo].[Product] SET write_time = CURRENT_TIMESTAMP
GO

ALTER TABLE [dbo].[Product] ADD CONSTRAINT CONSTRAINT_Product_write_time DEFAULT GETDATE() FOR write_time
GO

CREATE TRIGGER [dbo].[ProductUpdateTrigger]
ON [dbo].[Product]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.Product AS t
            INNER JOIN inserted AS i 
            ON t.ProdID = i.ProdID;
    END
END
GO


----
ALTER TABLE [dbo].[ShopIn] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [IdxUpdate_ShopIn] ON [dbo].[ShopIn] ([write_time])
GO

UPDATE [dbo].[ShopIn] SET write_time = CURRENT_TIMESTAMP
GO

ALTER TABLE [dbo].[ShopIn] ADD CONSTRAINT CONSTRAINT_ShopIn_write_time DEFAULT GETDATE() FOR write_time
GO

CREATE TRIGGER [dbo].[ShopInUpdateTrigger]
ON [dbo].[ShopIn]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.ShopIn AS t
            INNER JOIN inserted AS i 
            ON t.ID = i.ID;
    END
END
GO


----
ALTER TABLE [dbo].[ShopProcess] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [IdxUpdate_ShopProcess] ON [dbo].[ShopProcess] ([write_time])
GO

UPDATE [dbo].[ShopProcess] SET write_time = CURRENT_TIMESTAMP
GO

ALTER TABLE [dbo].[ShopProcess] ADD CONSTRAINT CONSTRAINT_ShopProcess_write_time DEFAULT GETDATE() FOR write_time
GO

CREATE TRIGGER [dbo].[ShopProcessUpdateTrigger]
ON [dbo].[ShopProcess]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.ShopProcess AS t
            INNER JOIN inserted AS i 
            ON t.ID = i.ID;
    END
END
GO


----
ALTER TABLE [dbo].[Supplier] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [IdxUpdate_Supplier] ON [dbo].[Supplier] ([write_time])
GO

UPDATE [dbo].[Supplier] SET write_time = CURRENT_TIMESTAMP
GO

ALTER TABLE [dbo].[Supplier] ADD CONSTRAINT CONSTRAINT_Supplier_write_time DEFAULT GETDATE() FOR write_time
GO

CREATE TRIGGER [dbo].[SupplierUpdateTrigger]
ON [dbo].[Supplier]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.Supplier AS t
            INNER JOIN inserted AS i 
            ON t.ID = i.ID;
    END
END
GO
