SELECT
	TO_CHAR(SYSDATE - INTERVAL '4' HOUR, 'HH24:MI') AS adjusted_time,
	~[current.time.no.colon] AS time_no_colon,
	((substr('~[current.time.no.colon]', 1, 2)) * 3600) AS HoursToSeconds,
	((substr('~[current.time.no.colon]', 3,2)) * 60) as MinutesToSeconds,
	(((substr('~[current.time.no.colon]', 1, 2)) * 3600) + ((substr('~[current.time.no.colon]', 3,2)) * 60)) as CurrentSeconds
	
FROM
	DUAL