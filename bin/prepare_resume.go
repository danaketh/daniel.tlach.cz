package main

import (
	"fmt"
	"log"
	"os" // Import the 'os' package
	"path/filepath"
	"sort"
	"strings"
	"time"

	"gopkg.in/yaml.v2"
)

type DateRange struct {
	Start   *time.Time `yaml:"start,omitempty"`   // Start date (pointer to handle potential null/omitted values)
	End     *time.Time `yaml:"end,omitempty"`     // End date (pointer to handle potential null/omitted values, especially if current=true)
	Current bool       `yaml:"current,omitempty"` // Whether the job is ongoing
}

type Job struct {
	Title        string    `yaml:"title"`                  // The job title
	Company      string    `yaml:"company,omitempty"`      // Company name (optional)
	Dates        DateRange `yaml:"range,omitempty"`        // Employment dates (optional)
	Description  string    `yaml:"description,omitempty"`  // General description (optional)
	Technologies []string  `yaml:"technologies,omitempty"` // List of technologies used (optional)
	Resume       bool      `yaml:"resume,omitempty"`
}

var latexReplacer = strings.NewReplacer(
	`\`, `\textbackslash{}`, // Must be escaped carefully
	`&`, `\&`,
	`%`, `\%`,
	`$`, `\$`,
	`#`, `\#`,
	`_`, `\_`,
	`{`, `\{`,
	`}`, `\}`,
	`~`, `\textasciitilde{}`, // Requires textcomp package in LaTeX usually
	`^`, `\textasciicircum{}`, // Requires textcomp package in LaTeX usually
)

func main() {
	yamlDir := "data/jobs"

	dirEntries, err := os.ReadDir(yamlDir)
	if err != nil {
		log.Fatalf("Failed to read directory: %v", err)
	}

	sort.Slice(dirEntries, func(i, j int) bool {
		return dirEntries[i].Name() > dirEntries[j].Name()
	})

	var jobs []Job

	for _, entry := range dirEntries {
		if entry.IsDir() || filepath.Ext(entry.Name()) != ".yaml" {
			continue
		}

		filePath := filepath.Join(yamlDir, entry.Name())
		yamlFile, err := os.ReadFile(filePath)
		if err != nil {
			log.Printf("Failed to read file %s: %v", entry.Name(), err)
			continue
		}

		var job Job
		err = yaml.Unmarshal(yamlFile, &job)
		if err != nil {
			log.Printf("Failed to unmarshal file %s: %v", entry.Name(), err)
			continue
		}

		jobs = append(jobs, job)
	}

	err = os.WriteFile("resume/experience.tex", []byte(generateRegularExperience(jobs)), 0644)
	if err != nil {
		log.Fatalf("Failed to write LaTeX file: %v", err)
	}

	err = os.WriteFile("resume/experience_full.tex", []byte(generateFullExperience(jobs)), 0644)
	if err != nil {
		log.Fatalf("Failed to write LaTeX file: %v", err)
	}

	fmt.Println("LaTeX files generated successfully!")
}

func EscapeLaTeX(s string) string {
	return latexReplacer.Replace(s)
}

func generateRegularExperience(jobs []Job) string {
	var sb strings.Builder

	for _, job := range jobs {
		if !job.Resume {
			continue // Skip jobs not marked for resume
		}
		// Begin entry
		sb.WriteString("\\entry\n")
		// Date
		var endDateDisplay string
		if job.Dates.Current {
			endDateDisplay = "Present"
		} else {
			endDateDisplay = job.Dates.End.Format("1/2006")
		}
		fmt.Fprintf(&sb, "    {%s - %s}\n", job.Dates.Start.Format("1/2006"), endDateDisplay)
		// Position
		fmt.Fprintf(&sb, "    {%s}\n", strings.TrimSpace(job.Title))
		// Company
		fmt.Fprintf(&sb, "    {%s}\n", strings.TrimSpace(job.Company))
		// Description and skills
		fmt.Fprintf(&sb, "    {%s\\\\ ", strings.TrimSpace(EscapeLaTeX(job.Description)))
		if len(job.Technologies) > 0 {
			for i, tech := range job.Technologies {
				fmt.Fprintf(&sb, "\\texttt{%s}", EscapeLaTeX(tech))
				if i < len(job.Technologies)-1 {
					sb.WriteString("\\slashsep") // Add the separator and a space
				}
			}
			sb.WriteString("}\n")
		}
	}

	return sb.String()
}

func generateFullExperience(jobs []Job) string {
	var sb strings.Builder

	for _, job := range jobs {
		// Begin entry
		sb.WriteString("\\entry\n")
		// Date
		var endDateDisplay string
		if job.Dates.Current {
			endDateDisplay = "Present"
		} else {
			endDateDisplay = job.Dates.End.Format("1/2006")
		}
		fmt.Fprintf(&sb, "    {%s - %s}\n", job.Dates.Start.Format("1/2006"), endDateDisplay)
		// Position
		fmt.Fprintf(&sb, "    {%s}\n", strings.TrimSpace(job.Title))
		// Company
		fmt.Fprintf(&sb, "    {%s}\n", strings.TrimSpace(job.Company))
		// Description and skills
		fmt.Fprintf(&sb, "    {%s\\\\ ", strings.TrimSpace(EscapeLaTeX(job.Description)))
		if len(job.Technologies) > 0 {
			for i, tech := range job.Technologies {
				fmt.Fprintf(&sb, "\\texttt{%s}", EscapeLaTeX(tech))
				if i < len(job.Technologies)-1 {
					sb.WriteString("\\slashsep") // Add the separator and a space
				}
			}
			sb.WriteString("}\n")
		}
	}

	return sb.String()
}
