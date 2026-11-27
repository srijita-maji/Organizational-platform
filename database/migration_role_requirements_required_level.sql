-- =============================================================================
-- Migration: Add required_level column to ed_job_role_skills
-- Target Database: TiDB Cloud / MySQL (workforce_knowledge_intelligence)
-- Purpose: Support role-specific required benchmark proficiency levels for HR
-- =============================================================================

-- TiDB Cloud syntax (TiDB natively supports IF NOT EXISTS for ADD COLUMN):
ALTER TABLE ed_job_role_skills 
ADD COLUMN IF NOT EXISTS required_level TINYINT NOT NULL DEFAULT 3;

-- For MySQL engines that do not support IF NOT EXISTS on ALTER TABLE,
-- run this if the column is not yet added:
-- ALTER TABLE ed_job_role_skills ADD COLUMN required_level TINYINT NOT NULL DEFAULT 3;

-- Optional: Synchronize existing mapped skills to match their category/skill default benchmark:
UPDATE ed_job_role_skills jrs
JOIN ed_skills s ON s.skill_id = jrs.skill_id
SET jrs.required_level = COALESCE(s.default_required_level, 3)
WHERE jrs.required_level IS NULL OR jrs.required_level = 0;
