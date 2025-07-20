package middleware

import (
	"net/http"
	"strings"
	"nareshka-backend/app/config"
	"nareshka-backend/app/shared/entities"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"gorm.io/gorm"
)

type AuthMiddleware struct {
	db  *gorm.DB
	cfg *config.Config
}

func NewAuthMiddleware(db *gorm.DB, cfg *config.Config) *AuthMiddleware {
	return &AuthMiddleware{
		db:  db,
		cfg: cfg,
	}
}

func (m *AuthMiddleware) RequireAuth() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		token := c.GetHeader("Authorization")
		if token == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header required"})
			c.Abort()
			return
		}

		userID, err := m.validateToken(token)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
			c.Abort()
			return
		}

		// Set user ID in context
		c.Set("user_id", userID)
		c.Next()
	})
}

func (m *AuthMiddleware) RequireRole(roles ...string) gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		userID, exists := c.Get("user_id")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
			c.Abort()
			return
		}

		var user entities.User
		if err := m.db.First(&user, userID).Error; err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "User not found"})
			c.Abort()
			return
		}

		// Check if user has required role
		userRole := string(user.Role)
		for _, role := range roles {
			if userRole == role {
				c.Set("user", user)
				c.Next()
				return
			}
		}

		c.JSON(http.StatusForbidden, gin.H{"error": "Insufficient permissions"})
		c.Abort()
	})
}

func (m *AuthMiddleware) OptionalAuth() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		token := c.GetHeader("Authorization")
		if token != "" {
			if userID, err := m.validateToken(token); err == nil {
				c.Set("user_id", userID)
				
				var user entities.User
				if err := m.db.First(&user, userID).Error; err == nil {
					c.Set("user", user)
				}
			}
		}
		c.Next()
	})
}

func (m *AuthMiddleware) validateToken(tokenString string) (uint, error) {
	// Remove "Bearer " prefix if present
	if strings.HasPrefix(tokenString, "Bearer ") {
		tokenString = strings.TrimPrefix(tokenString, "Bearer ")
	}

	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, jwt.ErrSignatureInvalid
		}
		return []byte(m.cfg.Auth.JWTSecret), nil
	})

	if err != nil {
		return 0, err
	}

	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		if userID, ok := claims["user_id"].(float64); ok {
			return uint(userID), nil
		}
	}

	return 0, jwt.ErrInvalidKey
}