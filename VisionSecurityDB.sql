USE master;
GO

IF EXISTS (SELECT name FROM sys.databases WHERE name = N'VisionSecurityDB')
BEGIN
    ALTER DATABASE VisionSecurityDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE VisionSecurityDB;
END
GO

CREATE DATABASE VisionSecurityDB;
GO

USE VisionSecurityDB;
GO

CREATE TABLE BiometricAudit (
    EventID INT IDENTITY(1,1) PRIMARY KEY,
    CaptureTimestamp DATETIME DEFAULT GETDATE(),
    VerificationStatus VARCHAR(50) NOT NULL, 
    ConfidenceScore FLOAT NOT NULL,         
    RawVideoFilename VARCHAR(255) NOT NULL, 
    RawVideoPath VARCHAR(500) NOT NULL,
    MeshVideoFilename VARCHAR(255) NOT NULL,
    MeshVideoPath VARCHAR(500) NOT NULL,
    HardwareSource VARCHAR(100) DEFAULT 'IPHONE_16_PRO_MAX_OPTICAL_SENSOR',
    DetectionType VARCHAR(50) DEFAULT 'Dual_Liveness_Video_KYC'
);
GO

-- To select all columns and records from the biometric audit table
SELECT * FROM BiometricAudit;

-- To select specific telemetry columns for a lightweight dashboard view
SELECT EventID, CaptureTimestamp, VerificationStatus, ConfidenceScore 
FROM BiometricAudit;

-- To filter audits with a successful verification status
SELECT * FROM BiometricAudit 
WHERE VerificationStatus = 'SUCCESS';

-- To filter audits that failed the verification process
SELECT * FROM BiometricAudit 
WHERE VerificationStatus = 'FAILED';

-- To filter audits with a biometric confidence score greater than 98 percent
SELECT * FROM BiometricAudit 
WHERE ConfidenceScore > 0.98;

-- To get the latest audits ordered by capture timestamp descending
SELECT * FROM BiometricAudit 
ORDER BY CaptureTimestamp DESC;

-- To get the top 5 audits with the highest confidence scores
SELECT TOP 5 * FROM BiometricAudit 
ORDER BY ConfidenceScore DESC;

-- To count the total number of recorded biometric events
SELECT COUNT(EventID) AS TotalAudits 
FROM BiometricAudit;

-- To select a specific forensic audit record by its primary key
SELECT * FROM BiometricAudit 
WHERE EventID = 1;

-- To select all unique hardware sources used for biometric capture
SELECT DISTINCT HardwareSource 
FROM BiometricAudit;

-- To filter audits captured exactly today
SELECT * FROM BiometricAudit 
WHERE CAST(CaptureTimestamp AS DATE) = CAST(GETDATE() AS DATE);

-- To search for audits where the raw video is stored in webm format
SELECT * FROM BiometricAudit 
WHERE RawVideoFilename LIKE '%.webm';

-- To calculate the overall average biometric confidence score across the entire system
SELECT AVG(ConfidenceScore) AS AverageConfidence 
FROM BiometricAudit;

-- To group audits by verification status and count the total events per status
SELECT VerificationStatus, COUNT(EventID) AS TotalCount 
FROM BiometricAudit 
GROUP BY VerificationStatus;

-- To calculate the maximum, minimum, and average confidence score grouped by hardware source
SELECT HardwareSource, 
       MAX(ConfidenceScore) AS MaxScore, 
       MIN(ConfidenceScore) AS MinScore, 
       AVG(ConfidenceScore) AS AvgScore 
FROM BiometricAudit 
GROUP BY HardwareSource;

-- To find high-risk audits with a confidence score lower than the overall system average
SELECT * FROM BiometricAudit 
WHERE ConfidenceScore < (SELECT AVG(ConfidenceScore) FROM BiometricAudit);

-- To count the number of biometric captures grouped by day to monitor traffic spikes
SELECT CAST(CaptureTimestamp AS DATE) AS AuditDate, COUNT(EventID) AS DailyCount 
FROM BiometricAudit 
GROUP BY CAST(CaptureTimestamp AS DATE) 
ORDER BY AuditDate DESC;

-- To extract the year and month from the timestamp and summarize total audits per month
SELECT YEAR(CaptureTimestamp) AS AuditYear, MONTH(CaptureTimestamp) AS AuditMonth, COUNT(EventID) AS MonthlyAudits 
FROM BiometricAudit 
GROUP BY YEAR(CaptureTimestamp), MONTH(CaptureTimestamp) 
ORDER BY AuditYear DESC, AuditMonth DESC;

-- To assign a ranking to audits based on their confidence score using a window function
SELECT EventID, HardwareSource, ConfidenceScore, 
       RANK() OVER(ORDER BY ConfidenceScore DESC) AS ConfidenceRank 
FROM BiometricAudit;