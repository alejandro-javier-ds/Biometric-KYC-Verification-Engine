IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'VisionSecurityDB')
BEGIN
    CREATE DATABASE VisionSecurityDB;
END
GO

USE VisionSecurityDB;
GO

IF OBJECT_ID('BiometricAudit', 'U') IS NOT NULL
BEGIN
    DROP TABLE BiometricAudit;
END
GO

CREATE TABLE BiometricAudit (
    EventID INT IDENTITY(1,1) PRIMARY KEY,
    CaptureTimestamp DATETIME DEFAULT GETDATE(),
    EvidenceFilename VARCHAR(255) NOT NULL,
    EvidencePath VARCHAR(500) NOT NULL,
    DetectionType VARCHAR(50) DEFAULT 'Liveness_Video_KYC'
);
GO

SELECT * FROM BiometricAudit;