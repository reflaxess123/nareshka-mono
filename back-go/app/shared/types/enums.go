package types

type UserRole string

const (
	UserRoleGuest UserRole = "GUEST"
	UserRoleUser  UserRole = "USER"
	UserRoleAdmin UserRole = "ADMIN"
)

type DifficultyLevel string

const (
	DifficultyBeginner     DifficultyLevel = "BEGINNER"
	DifficultyIntermediate DifficultyLevel = "INTERMEDIATE"
	DifficultyAdvanced     DifficultyLevel = "ADVANCED"
	DifficultyExpert       DifficultyLevel = "EXPERT"
)

type TaskStatus string

const (
	TaskStatusPending   TaskStatus = "PENDING"
	TaskStatusInReview  TaskStatus = "IN_REVIEW"
	TaskStatusCompleted TaskStatus = "COMPLETED"
	TaskStatusRejected  TaskStatus = "REJECTED"
)

type LanguageType string

const (
	LanguagePython     LanguageType = "python"
	LanguageJavaScript LanguageType = "javascript"
	LanguageJava       LanguageType = "java"
	LanguageCPP        LanguageType = "cpp"
	LanguageGo         LanguageType = "go"
	LanguageRust       LanguageType = "rust"
	LanguageC          LanguageType = "c"
	LanguageCSharp     LanguageType = "csharp"
)

type ContentType string

const (
	ContentTypeTask     ContentType = "TASK"
	ContentTypeTheory   ContentType = "THEORY"
	ContentTypeArticle  ContentType = "ARTICLE"
	ContentTypeVideo    ContentType = "VIDEO"
	ContentTypeQuiz     ContentType = "QUIZ"
)

type ReviewAnswer string

const (
	ReviewAnswerAgain ReviewAnswer = "AGAIN"
	ReviewAnswerHard  ReviewAnswer = "HARD"
	ReviewAnswerGood  ReviewAnswer = "GOOD"
	ReviewAnswerEasy  ReviewAnswer = "EASY"
)