package database

import (
	"fmt"
	"log"
	"nareshka-backend/app/config"
	"nareshka-backend/app/shared/entities"
	
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

func NewDatabase(cfg *config.Config) (*gorm.DB, error) {
	dsn := fmt.Sprintf(
		"host=%s user=%s password=%s dbname=%s port=%d sslmode=%s",
		cfg.Database.Host,
		cfg.Database.User,
		cfg.Database.Password,
		cfg.Database.Name,
		cfg.Database.Port,
		cfg.Database.SSLMode,
	)

	var gormLogger logger.Interface
	if cfg.Server.Env == "development" {
		gormLogger = logger.Default.LogMode(logger.Info)
	} else {
		gormLogger = logger.Default.LogMode(logger.Silent)
	}

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: gormLogger,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	// Enable extensions
	if err := db.Exec("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"").Error; err != nil {
		log.Printf("Warning: failed to create uuid-ossp extension: %v", err)
	}

	// Auto migrate the schema
	if err := AutoMigrate(db); err != nil {
		return nil, fmt.Errorf("failed to migrate database: %w", err)
	}

	return db, nil
}

func AutoMigrate(db *gorm.DB) error {
	// User models
	if err := db.AutoMigrate(
		&entities.User{},
		&entities.UserSession{},
		&entities.UserPreferences{},
	); err != nil {
		return err
	}

	// Content models  
	if err := db.AutoMigrate(
		&entities.ContentFile{},
		&entities.ContentBlock{},
		&entities.TheoryCard{},
		&entities.UserTheoryProgress{},
	); err != nil {
		return err
	}

	// Task models
	if err := db.AutoMigrate(
		&entities.Task{},
		&entities.TestCase{},
		&entities.TaskAttempt{},
		&entities.TaskSolution{},
	); err != nil {
		return err
	}

	// Progress models
	if err := db.AutoMigrate(
		&entities.UserContentProgress{},
		&entities.UserCategoryProgress{},
		&entities.UserPathProgress{},
		&entities.UserActivity{},
		&entities.UserStreak{},
	); err != nil {
		return err
	}

	return nil
}