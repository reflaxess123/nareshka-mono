package dto

type UpdateActivityRequest struct {
	ActivityType string                 `json:"activity_type" binding:"required"`
	EntityType   string                 `json:"entity_type,omitempty"`
	EntityID     *uint                  `json:"entity_id,omitempty"`
	Description  string                 `json:"description,omitempty"`
	PointsEarned int                    `json:"points_earned,omitempty"`
	Metadata     map[string]interface{} `json:"metadata,omitempty"`
}

type ProgressFilterRequest struct {
	UserID       *uint  `form:"user_id"`
	Category     string `form:"category"`
	ActivityType string `form:"activity_type"`
	StartDate    string `form:"start_date"`
	EndDate      string `form:"end_date"`
	Page         int    `form:"page,default=1"`
	Limit        int    `form:"limit,default=20"`
}

type CategoryProgressRequest struct {
	Category string `json:"category" binding:"required"`
}

type PathProgressRequest struct {
	PathName string `json:"path_name" binding:"required"`
}