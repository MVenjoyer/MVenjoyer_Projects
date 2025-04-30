package watcher

import (
	"context"
	"errors"
	"fmt"
	"io/fs"
	"path/filepath"
	"sync"
	"time"
)

type EventType string

const (
	EventTypeFileCreate  EventType = "file_created"
	EventTypeFileRemoved EventType = "file_removed"
)

var ErrDirNotExist = errors.New("dir does not exist")

type Event struct {
	Type EventType
	Path string
}

type Watcher struct {
	Events          chan Event
	refreshInterval time.Duration
	files           map[string]struct{}
	mu              sync.RWMutex
}

func NewDirWatcher(refreshInterval time.Duration) *Watcher {
	return &Watcher{
		refreshInterval: refreshInterval,
		Events:          make(chan Event),
		files:           make(map[string]struct{}),
	}
}

func (w *Watcher) walkFileTree(dirName string) (map[string]struct{}, error) {
	w.mu.Lock()
	defer w.mu.Unlock()
	files := make(map[string]struct{})
	err := filepath.Walk(dirName, func(path string, info fs.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() {
			files[path] = struct{}{}
		}
		return nil
	})
	if err != nil {
		return nil, err
	}
	return files, nil
}

func (w *Watcher) compare(cur *map[string]struct{}) {
	changed := false
	w.mu.RLock()
	defer w.mu.RUnlock()
	for path := range *cur {
		if _, ok := w.files[path]; !ok {
			changed = true
			w.Events <- Event{Type: EventTypeFileCreate, Path: path}
		}
	}
	for path := range w.files {
		if _, ok := (*cur)[path]; !ok {
			changed = true
			w.Events <- Event{Type: EventTypeFileRemoved, Path: path}
		}
	}
	if changed {
		w.files = *cur
	}
}

func (w *Watcher) WatchDir(ctx context.Context, path string) error {
	var wg sync.WaitGroup
	ticker := time.NewTicker(w.refreshInterval)
	defer ticker.Stop()
	files, err := w.walkFileTree(path)
	if err != nil {
		return ErrDirNotExist
	}

	w.mu.Lock()
	w.files = files
	w.mu.Unlock()
	for {
		select {
		case <-ctx.Done():
			wg.Wait()
			return ctx.Err()
		case <-ticker.C:
			wg.Add(1)
			go func() {
				defer wg.Done()
				cur, err := w.walkFileTree(path)
				if err != nil {
					_ = fmt.Errorf("error walking file tree: %w", err)
				}
				w.compare(&cur)
			}()
		}
	}
}

func (w *Watcher) Close() {
	close(w.Events)
}
