package services

import (
	"errors"
	"time"
	"nareshka-backend/app/config"
	"nareshka-backend/app/shared/entities"
	"nareshka-backend/app/shared/types"
	"nareshka-backend/app/features/auth/dto"

	"github.com/golang-jwt/jwt/v5"
	"github.com/redis/go-redis/v9"
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
)

type AuthService struct {
	db    *gorm.DB
	redis *redis.Client
	cfg   *config.Config
}

func NewAuthService(db *gorm.DB, redis *redis.Client, cfg *config.Config) *AuthService {
	return &AuthService{
		db:    db,
		redis: redis,
		cfg:   cfg,
	}
}

func (s *AuthService) Register(req *dto.RegisterRequest) (*dto.AuthResponse, error) {
	// Check if user already exists
	var existingUser entities.User
	if err := s.db.Where("email = ? OR username = ?", req.Email, req.Username).First(&existingUser).Error; err == nil {
		return nil, errors.New("user already exists")
	}

	// Hash password
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}

	// Create user
	newUser := entities.User{
		Username:     req.Username,
		Email:        req.Email,
		PasswordHash: string(hashedPassword),
		Role:         types.UserRoleUser,
		IsActive:     true,
	}

	if err := s.db.Create(&newUser).Error; err != nil {
		return nil, err
	}

	// Generate JWT token
	token, err := s.generateJWTToken(newUser.ID)
	if err != nil {
		return nil, err
	}

	return &dto.AuthResponse{
		User:  &newUser,
		Token: token,
	}, nil
}

func (s *AuthService) Login(req *dto.LoginRequest) (*dto.AuthResponse, error) {
	// Find user
	var foundUser entities.User
	if err := s.db.Where("email = ? OR username = ?", req.Login, req.Login).First(&foundUser).Error; err != nil {
		return nil, errors.New("invalid credentials")
	}

	// Check password
	if err := bcrypt.CompareHashAndPassword([]byte(foundUser.PasswordHash), []byte(req.Password)); err != nil {
		return nil, errors.New("invalid credentials")
	}

	// Generate JWT token
	token, err := s.generateJWTToken(foundUser.ID)
	if err != nil {
		return nil, err
	}

	return &dto.AuthResponse{
		User:  &foundUser,
		Token: token,
	}, nil
}

func (s *AuthService) Logout(token string) error {
	// In a real implementation, you might want to blacklist the token
	// For now, we'll just return success
	return nil
}

func (s *AuthService) GetCurrentUser(tokenString string) (*entities.User, error) {
	// Parse and validate JWT token
	userID, err := s.validateJWTToken(tokenString)
	if err != nil {
		return nil, err
	}

	// Find user
	var foundUser entities.User
	if err := s.db.First(&foundUser, userID).Error; err != nil {
		return nil, errors.New("user not found")
	}

	return &foundUser, nil
}

func (s *AuthService) generateJWTToken(userID uint) (string, error) {
	claims := jwt.MapClaims{
		"user_id": userID,
		"exp":     time.Now().Add(time.Hour * 24 * 7).Unix(), // 7 days
		"iat":     time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(s.cfg.Auth.JWTSecret))
}

func (s *AuthService) validateJWTToken(tokenString string) (uint, error) {
	// Remove "Bearer " prefix if present
	if len(tokenString) > 7 && tokenString[:7] == "Bearer " {
		tokenString = tokenString[7:]
	}

	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, errors.New("unexpected signing method")
		}
		return []byte(s.cfg.Auth.JWTSecret), nil
	})

	if err != nil {
		return 0, err
	}

	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		if userID, ok := claims["user_id"].(float64); ok {
			return uint(userID), nil
		}
	}

	return 0, errors.New("invalid token")
}