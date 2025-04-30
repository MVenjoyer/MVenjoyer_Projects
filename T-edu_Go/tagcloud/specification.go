package tagcloud

import "sort"

// TagCloud aggregates statistics about used tags
type TagCloud struct {
	Cloud map[string]int
}

// TagStat represents statistics regarding single tag
type TagStat struct {
	Tag             string
	OccurrenceCount int
}

// New should create a valid TagCloud instance
func New() *TagCloud {
	return &TagCloud{Cloud: make(map[string]int)}
}

// AddTag should add a tag to the cloud if it wasn't present and increase tag occurrence count
// thread-safety is not needed
func (t *TagCloud) AddTag(key string) {
	t.Cloud[key]++
}

// TopN should return top N most frequent tags ordered in descending order by occurrence count
// if there are multiple tags with the same occurrence count then the order is defined by implementation
// if n is greater that TagCloud size then all elements should be returned
// thread-safety is not needed
// there are no restrictions on time complexity
func (t *TagCloud) TopN(n int) []TagStat {
	sz := len(t.Cloud)
	if sz == 0 {
		return nil
	}
	answer := make([]TagStat, 0, sz)
	for key, value := range t.Cloud {
		answer = append(answer, TagStat{Tag: key, OccurrenceCount: value})
	}
	sort.Slice(answer, func(i, j int) bool {
		return answer[i].OccurrenceCount > answer[j].OccurrenceCount
	})
	if sz < n {
		return answer
	}
	return answer[:n]
}
