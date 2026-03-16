package extract

import (
	"bytes"
	"fmt"
	"net/url"

	"github.com/PuerkitoBio/goquery"
	readability "github.com/go-shiori/go-readability"
)

type Article struct {
	Title      string
	Text       string
	Discovered []string
}

// Extract extracts main article text using go-readability, optionally refines
// it via a CSS selector, and (optionally) discovers links from the HTML.
func Extract(pageURL *url.URL, htmlbytes []byte, selector string, discoverLinks bool) (Article, error) {
	article, err := readability.FromReader(bytes.NewReader(htmlbytes), pageURL)
	if err != nil {
		return Article{}, err
	}

	out := Article{
		Title: article.Title,
		Text:  article.TextContent,
	}

	if selector == "" && !discoverLinks {
		return out, nil
	}

	doc, err := goquery.NewDocumentFromReader(bytes.NewReader(htmlbytes))
	if err != nil {
		return out, nil
	}

	if selector != "" {
		selected := doc.Find(selector).Text()
		if selected != "" {
			out.Text = selected
		}
	}

	if discoverLinks {
		doc.Find("a[href]").Each(func(_ int, s *goquery.Selection) {
			href, ok := s.Attr("href")
			if !ok || href == "" {
				return
			}
			u, err := pageURL.Parse(href)
			if err != nil {
				return
			}
			out.Discovered = append(out.Discovered, u.String())
		})
	} else {
		out.Discovered = []string{}
		fmt.Println("pageurl:", pageURL.String(), "discoverLinks is false")
	}

	return out, nil
}
