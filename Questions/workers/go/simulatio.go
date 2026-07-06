package main

import (
	"fmt"
	"slices"
	"strings"
)

type WorkerRegistration struct {
	w    map[string]*Worker
	ts   []int
	topN []*Worker // can be used as MinHeap for optimal
}

type Worker struct {
	Id        string
	Career    *Career
	Promotion *Role
	Reg       [][3]int
	Worked    int
	Earned    int
}

type Role struct {
	Position     string
	Compensation int
	createdAt    int
}

type Career struct {
	roles []*Role
	hm    map[string]*Role
}

const INV = "invalid_request"
const OKREG = "registered"
const OKPROM = "success"

func (wr *WorkerRegistration) AddWorker(workerId string, position string, compensation int) bool {
	if _, exists := wr.w[workerId]; exists {
		return false
	}
	wr.w[workerId] = &Worker{
		Id: workerId,
		Career: &Career{
			roles: []*Role{
				{
					Position:     position,
					Compensation: compensation,
					createdAt:    0,
				},
			},
			hm: make(map[string]*Role),
		},
		Promotion: nil,
		Reg:       [][3]int{},
	}
	wr.topN = append(wr.topN, wr.w[workerId])
	wr.sort()
	return true
}

func (wr *WorkerRegistration) Register(workerId string, timestamp int) string {
	if _, exists := wr.w[workerId]; !exists {
		return INV
	}
	p := wr.w[workerId]
	if len(p.Reg) == 0 || p.Reg[len(p.Reg)-1][1] != -1 {
		// Add promotion to career
		if p.Promotion != nil && p.Promotion.createdAt <= timestamp {
			p.Promotion.createdAt = timestamp
			p.Career.roles = append(p.Career.roles, p.Promotion)
			p.Promotion = nil
		}

		// add begin of day
		p.Reg = append(p.Reg, [3]int{timestamp, -1, -1})
		return OKREG
	}
	p.Reg[len(p.Reg)-1][1] = timestamp
	p.Reg[len(p.Reg)-1][2] = p.Career.roles[len(p.Career.roles)-1].Compensation

	p.Worked += timestamp - p.Reg[len(p.Reg)-1][0]
	wr.sort()
	return OKREG
}

func (wr *WorkerRegistration) Get(workerId string) string {
	if _, exists := wr.w[workerId]; !exists {
		return ""
	}
	p := wr.w[workerId]
	return fmt.Sprintf("%d", p.Worked)
}

func (wr *WorkerRegistration) TopNWorkers(n int, position string) string {
	if len(wr.topN) == 0 || n <= 0 {
		return ""
	}
	// filter by current position
	filtered := []*Worker{}
	for _, w := range wr.topN {
		if w.Career != nil && len(w.Career.roles) > 0 &&
			w.Career.roles[len(w.Career.roles)-1].Position == position {
			filtered = append(filtered, w)
		}
	}
	res := ""
	if len(filtered) == 0 {
		return res
	}
	l := min(n, len(filtered))
	for _, w := range filtered[:l-1] {
		res += fmt.Sprintf("%s(%d), ", w.Id, w.Worked)
	}
	res += fmt.Sprintf("%s(%d)", filtered[l-1].Id, filtered[l-1].Worked)
	return res
}

func (wr *WorkerRegistration) sort() {
	slices.SortFunc(wr.topN, func(a, b *Worker) int {
		if a.Worked != b.Worked {
			return b.Worked - a.Worked

		}
		return strings.Compare(a.Id, b.Id)
	})
}

func (wr *WorkerRegistration) Promote(workerId string, position string, compensation int, timestamp int) string {
	if _, exists := wr.w[workerId]; !exists {
		return INV
	}
	p := wr.w[workerId]
	if p.Promotion != nil {
		return INV
	}
	p.Promotion = &Role{
		Position:     position,
		Compensation: compensation,
		createdAt:    timestamp,
	}
	return OKPROM
}

func (wr *WorkerRegistration) CalcSalary(workerId string, start, end int) string {
	if _, exists := wr.w[workerId]; !exists {
		return ""
	}
	// get first registration that is before or equal to start
	p := wr.w[workerId]
	salary := 0
	for _, r := range p.Reg {
		if r[1] == -1 {
			continue
		}
		if r[0] >= start && r[1] <= end {
			salary += (r[1] - r[0]) * r[2]
		} else if r[0] < start && r[1] > end {
			salary += (end - start) * r[2]
		} else if r[0] < start && r[1] > start {
			salary += (r[1] - start) * r[2]
		} else if r[0] < end && r[1] > end {
			salary += (end - r[0]) * r[2]
		}
	}
	return fmt.Sprintf("%d", salary)
}
