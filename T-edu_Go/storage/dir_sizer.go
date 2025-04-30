package storage

import (
	"context"
	"sync/atomic"

	"golang.org/x/sync/errgroup"
)

type Result struct {
	Size  int64
	Count int64
}
type DirSizer interface {
	Size(ctx context.Context, d Dir) (Result, error)
}

type sizer struct {
	maxWorkersCount int
}

type options struct {
	file  File
	dir   Dir
	group *errgroup.Group
	ctx   context.Context
	count *int64
	sum   *int64
}

func (o *options) getNew(file File, dir Dir) options {
	return options{file: file, dir: dir, ctx: o.ctx, group: o.group, sum: o.sum, count: o.count}
}

func NewSizer() DirSizer {
	return &sizer{
		maxWorkersCount: 20,
	}
}

func (s *sizer) Size(ctx context.Context, d Dir) (Result, error) {
	group, ctx := errgroup.WithContext(ctx)
	group.SetLimit(s.maxWorkersCount)
	var sum, count int64
	group.Go(func() error {
		return s.processDir(options{group: group, file: nil, dir: d, ctx: ctx, sum: &sum, count: &count})
	})
	if err := group.Wait(); err != nil {
		return Result{}, err
	}
	return Result{Size: sum, Count: count}, nil
}

func (s *sizer) processDir(options options) error {
	dirs, files, err := options.dir.Ls(options.ctx)
	if err != nil {
		return err
	}
	options.group.Go(func() error {
		for _, file := range files {
			options.group.Go(func() error {
				return s.processFile(options.getNew(file, nil))
			})
		}
		return nil
	})
	options.group.Go(func() error {
		for _, dir := range dirs {
			options.group.Go(func() error {
				return s.processDir(options.getNew(nil, dir))
			})
		}
		return nil
	})
	return nil
}

func (s *sizer) processFile(options options) error {
	stat, err := options.file.Stat(options.ctx)
	if err != nil {
		return err
	}
	atomic.AddInt64(options.count, 1)
	atomic.AddInt64(options.sum, stat)
	return nil
}
