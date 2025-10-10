package main

import (
	"fmt"
	"log"
	"os" // Import the 'os' package
	"path/filepath"
	"regexp"
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

// ConvertMarkdownLinksToLaTeX converts Markdown hyperlinks [text](url) to LaTeX \href{url}{text}
// and escapes all other LaTeX special characters in the string
func ConvertMarkdownLinksToLaTeX(s string) string {
	// Regex to match Markdown links: [text](url)
	re := regexp.MustCompile(`\[([^\]]+)\]\(([^)]+)\)`)

	// Track positions of markdown links to avoid escaping them
	var parts []string
	lastIndex := 0

	matches := re.FindAllStringSubmatchIndex(s, -1)
	for _, match := range matches {
		// Add the text before the link (escaped)
		if match[0] > lastIndex {
			parts = append(parts, EscapeLaTeX(s[lastIndex:match[0]]))
		}

		// Add the LaTeX href (with only the link text escaped)
		text := s[match[2]:match[3]]
		url := s[match[4]:match[5]]
		parts = append(parts, fmt.Sprintf(`\href{%s}{%s}`, url, EscapeLaTeX(text)))

		lastIndex = match[1]
	}

	// Add any remaining text after the last link (escaped)
	if lastIndex < len(s) {
		parts = append(parts, EscapeLaTeX(s[lastIndex:]))
	}

	return strings.Join(parts, "")
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
		// Convert Markdown links to LaTeX and escape special characters
		description := strings.TrimSpace(ConvertMarkdownLinksToLaTeX(job.Description))
		fmt.Fprintf(&sb, "    {%s\\\\ ", description)
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
		// Convert Markdown links to LaTeX and escape special characters
		description := strings.TrimSpace(ConvertMarkdownLinksToLaTeX(job.Description))
		fmt.Fprintf(&sb, "    {%s\\\\ ", description)
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
