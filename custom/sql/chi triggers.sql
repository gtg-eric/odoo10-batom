---- added write_time for tracking importing to odoo

----
ALTER TABLE [dbo].[comProduct] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [Idx_comProduct] ON [dbo].[comProduct] ([write_time])
GO

UPDATE [dbo].[comProduct] SET write_time = CURRENT_TIMESTAMP
GO

CREATE TRIGGER [dbo].[comProductUpdateTrigger]
ON [dbo].[comProduct]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.comProduct AS t
            INNER JOIN inserted AS i 
            ON t.ProdID = i.ProdID;
    END
END
GO


----
ALTER TABLE [dbo].[comProdRec] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [Idx_comProdRec] ON [dbo].[comProdRec] ([write_time])
GO

UPDATE [dbo].[comProdRec] SET write_time = CURRENT_TIMESTAMP
GO

CREATE TRIGGER [dbo].[comProdRecUpdateTrigger]
ON [dbo].[comProdRec]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.comProdRec AS t
            INNER JOIN inserted AS i 
            ON t.Flag = i.Flag AND t.BillNO = i.BillNO AND t.RowNO = i.RowNO;
    END
END
GO


----
ALTER TABLE [dbo].[comCustomer] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [Idx_comCustomer] ON [dbo].[comCustomer] ([write_time])
GO

UPDATE [dbo].[comCustomer] SET write_time = CURRENT_TIMESTAMP
GO

CREATE TRIGGER [dbo].[comCustomerUpdateTrigger]
ON [dbo].[comCustomer]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.comCustomer AS t
            INNER JOIN inserted AS i 
            ON t.Flag = i.Flag AND t.ID = i.ID;
    END
END
GO


----
ALTER TABLE [dbo].[comCustDesc] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [Idx_comCustDesc] ON [dbo].[comCustDesc] ([write_time])
GO

UPDATE [dbo].[comCustDesc] SET write_time = CURRENT_TIMESTAMP
GO

CREATE TRIGGER [dbo].[comCustDescUpdateTrigger]
ON [dbo].[comCustDesc]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.comCustDesc AS t
            INNER JOIN inserted AS i 
            ON t.Flag = i.Flag AND t.ID = i.ID;
    END
END
GO


----
ALTER TABLE [dbo].[comLinkMan] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [Idx_comLinkMan] ON [dbo].[comLinkMan] ([write_time])
GO

UPDATE [dbo].[comLinkMan] SET write_time = CURRENT_TIMESTAMP
GO

CREATE TRIGGER [dbo].[comLinkManUpdateTrigger]
ON [dbo].[comLinkMan]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.comLinkMan AS t
            INNER JOIN inserted AS i 
            ON t.Flag = i.Flag AND t.CustomID = i.CustomID AND t.RowNO = i.RowNO;
    END
END
GO


----
ALTER TABLE [dbo].[prdBOMMain] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [Idx_prdBOMMain] ON [dbo].[prdBOMMain] ([write_time])
GO

UPDATE [dbo].[prdBOMMain] SET write_time = CURRENT_TIMESTAMP
GO

CREATE TRIGGER [dbo].[prdBOMMainUpdateTrigger]
ON [dbo].[prdBOMMain]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.prdBOMMain AS t
            INNER JOIN inserted AS i 
            ON t.Flag = i.Flag AND
				t.ProductID = i.ProductID AND
				t.OrderID = i.OrderID AND
				t.ItemNo = i.ItemNo AND
				t.ConfigNO = i.ConfigNO AND
				t.MainConfigNo = i.MainConfigNo AND
				t.PreNodeProdID = i.PreNodeProdID AND
				t.NodeLevel = i.NodeLevel AND
				t.BOMMainRowNo = i.BOMMainRowNo;
    END
END
GO


----
ALTER TABLE [prdBOMMats] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [Idx_prdBOMMats] ON [dbo].[prdBOMMats] ([write_time])
GO

UPDATE [dbo].[prdBOMMats] SET write_time = CURRENT_TIMESTAMP
GO

CREATE TRIGGER [dbo].[prdBOMMatsUpdateTrigger]
ON [dbo].[prdBOMMats]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.prdBOMMats AS t
            INNER JOIN inserted AS i 
            ON t.Flag = i.Flag AND
				t.ProductID = i.ProductID AND
				t.OrderID = i.OrderID AND
				t.ItemNo = i.ItemNo AND
				t.RowNO = i.RowNO AND
				t.ConfigNO = i.ConfigNO AND
				t.MainConfigNo = i.MainConfigNo AND
				t.NodeLevel = i.NodeLevel AND
				t.BOMMainRowNO = i.BOMMainRowNO;
    END
END
GO


----
ALTER TABLE [prdBOMPgms] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [Idx_prdBOMPgms] ON [dbo].[prdBOMPgms] ([write_time])
GO

UPDATE [dbo].[prdBOMPgms] SET write_time = CURRENT_TIMESTAMP
GO

CREATE TRIGGER [dbo].[prdBOMPgmsUpdateTrigger]
ON [dbo].[prdBOMPgms]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.prdBOMPgms AS t
            INNER JOIN inserted AS i 
            ON t.Flag = i.Flag AND
				t.MainProdID = i.MainProdID AND
				t.OrderID = i.OrderID AND
				t.ItemNO = i.ItemNO AND
				t.RowNO = i.RowNO AND
				t.ConfigNO = i.ConfigNO AND
				t.MainConfigNo = i.MainConfigNo AND
				t.NodeLevel = i.NodeLevel AND
				t.BOMMainRowNo = i.BOMMainRowNo;
   END
END
GO


----
ALTER TABLE [dbo].[prdMakeProgram] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [Idx_prdMakeProgram] ON [dbo].[prdMakeProgram] ([write_time])
GO

UPDATE [dbo].[prdMakeProgram] SET write_time = CURRENT_TIMESTAMP
GO

CREATE TRIGGER [dbo].[prdMakeProgramUpdateTrigger]
ON [dbo].[prdMakeProgram]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.prdMakeProgram AS t
            INNER JOIN inserted AS i 
            ON t.ProgramID = i.ProgramID;
    END
END
GO


----
ALTER TABLE [dbo].[prdMkOrdMain] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [Idx_prdMkOrdMain] ON [dbo].[prdMkOrdMain] ([write_time])
GO

UPDATE [dbo].[prdMkOrdMain] SET write_time = CURRENT_TIMESTAMP
GO

CREATE TRIGGER [dbo].[prdMkOrdMainUpdateTrigger]
ON [dbo].[prdMkOrdMain]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.prdMkOrdMain AS t
            INNER JOIN inserted AS i 
            ON t.Flag = i.Flag AND t.MKOrdNO = i.MKOrdNO;
    END
END
GO


----
ALTER TABLE [dbo].[prdMkOrdMats] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [Idx_prdMkOrdMats] ON [dbo].[prdMkOrdMats] ([write_time])
GO

UPDATE [dbo].[prdMkOrdMats] SET write_time = CURRENT_TIMESTAMP
GO

CREATE TRIGGER [dbo].[prdMkOrdMatsUpdateTrigger]
ON [dbo].[prdMkOrdMats]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.prdMkOrdMats AS t
            INNER JOIN inserted AS i 
            ON t.Flag = i.Flag AND t.MkOrdNO = i.MkOrdNO AND t.RowNO = i.RowNO;
    END
END
GO


----
ALTER TABLE [dbo].[prdMkOrdPgms] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [Idx_prdMkOrdPgms] ON [dbo].[prdMkOrdPgms] ([write_time])
GO

UPDATE [dbo].[prdMkOrdPgms] SET write_time = CURRENT_TIMESTAMP
GO

CREATE TRIGGER [dbo].[prdMkOrdPgmsUpdateTrigger]
ON [dbo].[prdMkOrdPgms]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.prdMkOrdPgms AS t
            INNER JOIN inserted AS i 
            ON t.Flag = i.Flag AND t.MkOrdNO = i.MkOrdNO AND t.RowNO = i.RowNO AND t.FromRowNo = i.FromRowNo;
    END
END
GO


----
ALTER TABLE [dbo].[prdWareIn] ADD [write_time] DATETIME NULL
GO

CREATE INDEX [Idx_prdWareIn] ON [dbo].[prdWareIn] ([write_time])
GO

UPDATE [dbo].[prdWareIn] SET write_time = CURRENT_TIMESTAMP
GO

CREATE TRIGGER [dbo].[prdWareInUpdateTrigger]
ON [dbo].[prdWareIn]
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(write_time)
    BEGIN
        UPDATE t
            SET t.write_time = CURRENT_TIMESTAMP
            FROM dbo.prdWareIn AS t
            INNER JOIN inserted AS i 
            ON t.Flag = i.Flag AND t.WareInNO = i.WareInNO;
    END
END
GO


ALTER TABLE [dbo].[comCustDesc] ADD CONSTRAINT CONSTRAINT_comCustDesc_write_time DEFAULT GETDATE() FOR write_time
GO

ALTER TABLE [dbo].[comCustomer] ADD CONSTRAINT CONSTRAINT_comCustomer_write_time DEFAULT GETDATE() FOR write_time
GO

ALTER TABLE [dbo].[comLinkMan] ADD CONSTRAINT CONSTRAINT_comLinkMan_write_time DEFAULT GETDATE() FOR write_time
GO

ALTER TABLE [dbo].[comProdRec] ADD CONSTRAINT CONSTRAINT_comProdRec_write_time DEFAULT GETDATE() FOR write_time
GO

ALTER TABLE [dbo].[comProduct] ADD CONSTRAINT CONSTRAINT_comProduct_write_time DEFAULT GETDATE() FOR write_time
GO

ALTER TABLE [dbo].[prdBOMMain] ADD CONSTRAINT CONSTRAINT_prdBOMMain_write_time DEFAULT GETDATE() FOR write_time
GO

ALTER TABLE [dbo].[prdBOMMats] ADD CONSTRAINT CONSTRAINT_prdBOMMats_write_time DEFAULT GETDATE() FOR write_time
GO

ALTER TABLE [dbo].[prdBOMPgms] ADD CONSTRAINT CONSTRAINT_prdBOMPgms_write_time DEFAULT GETDATE() FOR write_time
GO

ALTER TABLE [dbo].[prdMakeProgram] ADD CONSTRAINT CONSTRAINT_prdMakeProgram_write_time DEFAULT GETDATE() FOR write_time
GO

ALTER TABLE [dbo].[prdMkOrdMain] ADD CONSTRAINT CONSTRAINT_prdMkOrdMain_write_time DEFAULT GETDATE() FOR write_time
GO

ALTER TABLE [dbo].[prdMkOrdMats] ADD CONSTRAINT CONSTRAINT_prdMkOrdMats_write_time DEFAULT GETDATE() FOR write_time
GO

ALTER TABLE [dbo].[prdMkOrdPgms] ADD CONSTRAINT CONSTRAINT_prdMkOrdPgms_write_time DEFAULT GETDATE() FOR write_time
GO

ALTER TABLE [dbo].[prdWareIn] ADD CONSTRAINT CONSTRAINT_prdWareIn_write_time DEFAULT GETDATE() FOR write_time
GO
