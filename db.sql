--
-- File generated with SQLiteStudio v3.4.4 on Wed Feb 26 17:07:36 2025
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: Department
CREATE TABLE IF NOT EXISTS Department (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Table: HealthCheckCard
CREATE TABLE IF NOT EXISTS HealthCheckCard (
    card_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Table: Session
CREATE TABLE IF NOT EXISTS Session (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    status TEXT CHECK(status IN ('Open', 'Closed')) NOT NULL
);

-- Table: Team
CREATE TABLE IF NOT EXISTS Team (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES Department(department_id) ON DELETE SET NULL
);

-- Table: UserTeamSummary
CREATE TABLE IF NOT EXISTS UserTeamSummary (
    user_id INTEGER PRIMARY KEY,
    total_teams INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- Table: Vote
CREATE TABLE IF NOT EXISTS Vote (
    vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    card_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,
    vote TEXT CHECK(vote IN ('Green', 'Amber', 'Red')) NOT NULL,
    comments TEXT,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES HealthCheckCard(card_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES Session(session_id) ON DELETE CASCADE
);

-- Trigger: track_user_progress
CREATE TRIGGER IF NOT EXISTS track_user_progress
AFTER INSERT ON Vote
FOR EACH ROW
BEGIN
    INSERT INTO UserProgress (user_id, total_votes)
    VALUES (NEW.user_id, 1)
    ON CONFLICT(user_id) DO UPDATE SET total_votes = total_votes + 1;
END;

-- Trigger: track_votes
CREATE TRIGGER IF NOT EXISTS track_votes
AFTER INSERT ON Vote
FOR EACH ROW
BEGIN
    INSERT INTO VoteSummary (session_id, total_votes)
    VALUES (NEW.session_id, 1)
    ON CONFLICT(session_id) DO UPDATE SET total_votes = total_votes + 1;
END;

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
