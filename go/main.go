package main

import (
	"flag"
	"fmt"
	"log"
	"os"

	"gopkg.in/yaml.v2"
)

// Configuration struct for general app configuration values
type Config struct {
	General struct {
		Log       string `yaml:"log"`
		Messages  string `yaml:"messages"`
		Whitelist string `yaml:"whitelist"`
	}
	Email struct {
		Polling uint `yaml:"polling"`
		IMAP    struct {
			Host string `yaml:"host"`
			SSL  bool   `yaml:"ssl"`
			Port uint16 `yaml:"port"`
		}
		SMTP struct {
			Host string `yaml:"host"`
			SSL  bool   `yaml:"ssl"`
			Port uint16 `yaml:"port"`
		}
	}
}

// Secrets struct for e-mail credentials
type Secrets struct {
	Email struct {
		Username string `yaml:"username"`
		Password string `yaml:"password"`
	}
}

func ReadYML(configPath string, configPointer interface{}) error {
	// Open config file
	file, err := os.Open(configPath)
	if err != nil {
		return err
	}
	defer file.Close()

	// Init new YAML decoder
	d := yaml.NewDecoder(file)
	if err := d.Decode(configPointer); err != nil {
		return err
	}

	return nil
}

// ValidateConfigPath just makes sure, that the path provided is a file,
// that can be read
func ValidateConfigPath(path string) error {
	s, err := os.Stat(path)
	if err != nil {
		return err
	}
	if s.IsDir() {
		return fmt.Errorf("'%s' is a directory, not a normal file", path)
	}
	return nil
}

// ParseFlags will create and parse the CLI flags
// and return the path to be used elsewhere
func ParseFlags() (string, string, error) {
	// String that contains the configured configuration path
	var configPath string
	var secretPath string

	// Set up a CLI flag called "-config" to allow users
	// to supply the configuration file
	flag.StringVar(&configPath, "config", "./config.yml", "path to config file")
	flag.StringVar(&secretPath, "secrets", "./secrets.yml", "path to secrets file")

	// Actually parse the flags
	flag.Parse()

	// Validate the path first
	if err := ValidateConfigPath(configPath); err != nil {
		return "", "", err
	}
	if err := ValidateConfigPath(secretPath); err != nil {
		return "", "", err
	}

	// Return the configuration path
	return configPath, secretPath, nil
}

func main() {
	fmt.Printf("running")
	configPath, secretPath, err := ParseFlags()
	if err != nil {
		log.Fatal(err)
	}

	config := &Config{}
	err = ReadYML(configPath, &config)
	if err != nil {
		log.Fatal(err)
	}

	secrets := &Secrets{}
	err = ReadYML(secretPath, &secrets)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Printf("%+v\n", config)

	fmt.Printf("%+v\n", secrets)

}
