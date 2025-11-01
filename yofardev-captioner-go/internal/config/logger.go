package config

import (
    "os"
    
    "github.com/sirupsen/logrus"
)

var Log *logrus.Logger

func InitLogger() {
    Log = logrus.New()
    Log.SetOutput(os.Stdout)
    Log.SetFormatter(&logrus.TextFormatter{
        FullTimestamp: true,
    })
    Log.SetLevel(logrus.InfoLevel)
}
