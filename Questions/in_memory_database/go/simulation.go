package main

import (
	"fmt"
	"sort"
	"strings"
)

type InMemoryDatabase struct {
	m        map[string]map[string]*TTLData
	reg      map[string]map[string]map[int64]TTLData
	timeline []int64
}

type TTLData struct {
	value    string
	expireAt int64
}

func (this *InMemoryDatabase) Get(key, field string) (string, error) {
	value, ok := this.m[key]
	if !ok {
		return "", nil
	}
	fieldValue, ok := value[field]
	if !ok {
		return "", nil
	}
	return (*fieldValue).value, nil
}

func (this *InMemoryDatabase) GetAt(key, field string, timestamp int64) (string, error) {
	this.timeline = append(this.timeline, timestamp)
	value, ok := this.m[key]
	if !ok {
		return "", nil
	}
	fieldValue, ok := value[field]
	if !ok {
		return "", nil
	}
	if this.HasExpired(key, field, timestamp) {
		return "", nil
	}
	return (*fieldValue).value, nil
}

func (this *InMemoryDatabase) Set(key, field, value string) string {
	if len(this.timeline) == 0 {
		this.timeline = append(this.timeline, 0)
		return this.SetAt(key, field, value, 0)
	}
	return this.SetAt(key, field, value, this.timeline[len(this.timeline)-1])
}

func (this *InMemoryDatabase) SetAt(key, field, value string, timestamp int64) string {
	return this.SetAtWithTTL(key, field, value, timestamp, -1)
}

func (this *InMemoryDatabase) SetAtWithTTL(key, field, value string, timestamp, ttl int64) string {
	this.timeline = append(this.timeline, timestamp)
	if _, ok := this.reg[key]; !ok {
		this.reg[key] = make(map[string]map[int64]TTLData)
		this.reg[key][field] = make(map[int64]TTLData)
	}
	if _, ok := this.reg[key][field]; !ok {
		this.reg[key][field] = make(map[int64]TTLData)
	}
	if ttl > 0 {
		this.reg[key][field][timestamp] = TTLData{value: value, expireAt: timestamp + ttl}
	} else {
		this.reg[key][field][timestamp] = TTLData{value: value, expireAt: -1}
	}

	aux := this.reg[key][field][timestamp]
	if _, ok := this.m[key]; !ok {
		this.m[key] = make(map[string]*TTLData)
		this.m[key][field] = &(aux)
		return ""
	}
	this.m[key][field] = &(aux)
	return ""
}

func (this *InMemoryDatabase) Delete(key, field string) string {
	_, ok := this.m[key]
	if _, okf := this.m[key][field]; ok && okf {
		delete(this.m[key], field)
		return "true"
	}
	return "false"
}

func (this *InMemoryDatabase) DeleteAt(key, field string, timestamp int64) string {
	this.timeline = append(this.timeline, timestamp)
	_, ok := this.m[key]
	if _, okf := this.m[key][field]; ok && okf && !this.HasExpired(key, field, timestamp) {
		delete(this.m[key], field)
		return "true"
	}
	return "false"
}

func (this *InMemoryDatabase) Scan(key string) string {
	return this.ScanByPrefix(key, "")
}

func (this *InMemoryDatabase) ScanByPrefix(key, prefix string) string {
	if _, ok := this.m[key]; !ok {
		return ""
	}
	sortedFields := make([]string, 0)
	for field := range this.m[key] {
		if strings.HasPrefix(field, prefix) {
			sortedFields = append(sortedFields, field)
		}
	}
	sort.Strings(sortedFields)
	result := ""
	if len(sortedFields) == 0 {
		return result
	}
	for _, field := range sortedFields[:len(sortedFields)-1] {
		value := this.m[key][field]
		result += fmt.Sprintf("%s(%s), ", field, value.value)
	}
	value := this.m[key][sortedFields[len(sortedFields)-1]]
	result += fmt.Sprintf("%s(%s)", sortedFields[len(sortedFields)-1], value.value)

	return result
}

func (this *InMemoryDatabase) ScanAt(key string, timestamp int64) string {
	return this.ScanByPrefixAt(key, "", timestamp)
}

func (this *InMemoryDatabase) ScanByPrefixAt(key, prefix string, timestamp int64) string {
	this.timeline = append(this.timeline, timestamp)
	if _, ok := this.m[key]; !ok {
		return ""
	}
	sortedFields := make([]string, 0)
	for field := range this.m[key] {
		if strings.HasPrefix(field, prefix) && !this.HasExpired(key, field, timestamp) {
			sortedFields = append(sortedFields, field)
		}
	}
	sort.Strings(sortedFields)
	result := ""
	if len(sortedFields) == 0 {
		return result
	}
	for _, field := range sortedFields[:len(sortedFields)-1] {
		value := this.m[key][field]
		result += fmt.Sprintf("%s(%s), ", field, value.value)
	}
	value := this.m[key][sortedFields[len(sortedFields)-1]]
	result += fmt.Sprintf("%s(%s)", sortedFields[len(sortedFields)-1], value.value)

	return result
}

func (this *InMemoryDatabase) HasExpired(key, field string, timestamp int64) bool {
	return this.m[key][field].expireAt != -1 && this.m[key][field].expireAt <= timestamp
}
