package dto

import "nareshka-backend/app/shared/entities"

type AuthResponse struct {
	User  *entities.User `json:"user"`
	Token string         `json:"token"`
}