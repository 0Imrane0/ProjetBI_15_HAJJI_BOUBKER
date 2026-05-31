-- Keep report categories usable for content-based and hybrid models.

UPDATE reports
SET business_category = 'general'
WHERE business_category IS NULL OR business_category = '';
