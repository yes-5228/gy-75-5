<script setup>
import { computed } from 'vue'
import DataTable from '../components/DataTable.vue'
import MetricGrid from '../components/MetricGrid.vue'
import SectionHeader from '../components/SectionHeader.vue'
import StatusBadge from '../components/StatusBadge.vue'

const props = defineProps({
  statistics: { type: Object, required: true },
  inspectionStatistics: { type: Object, required: true },
  plans: { type: Array, required: true },
  faults: { type: Array, required: true },
  elevators: { type: Array, required: true },
})

const metrics = computed(() => [
  { label: 'Elevators', value: props.elevators.length, hint: 'Assets in maintenance scope' },
  { label: 'Total Inspections', value: props.inspectionStatistics.totalInspections, hint: 'All inspection records' },
  { label: 'Open Faults', value: props.statistics.openFaults, hint: 'Pending, active, or review' },
  { label: 'Completed Repairs', value: props.statistics.completedFaults, hint: 'Closed repair tickets' },
])

const inspectionMetrics = computed(() => [
  { label: 'Normal', value: props.inspectionStatistics.normalCount, hint: '正常运行', status: 'Normal', level: 'normal' },
  { label: 'Slight Abnormal', value: props.inspectionStatistics.slightAbnormalCount, hint: '轻微异常', status: 'Slight Abnormal', level: 'slight' },
  { label: 'Severe Abnormal', value: props.inspectionStatistics.severeAbnormalCount, hint: '严重异常', status: 'Severe Abnormal', level: 'severe' },
])

const upcomingPlans = computed(() => props.plans.slice(0, 5))
const urgentFaults = computed(() => props.faults.filter((fault) => fault.priority !== 'Normal').slice(0, 5))
</script>

<template>
  <div class="view-stack">
    <MetricGrid :metrics="metrics" />

    <section class="panel">
      <SectionHeader title="Inspection Result Summary" description="Result grading and handling plan overview" />
      <div class="inspection-summary-grid">
        <div v-for="item in inspectionMetrics" :key="item.label" class="inspection-summary-card" :data-level="item.level">
          <StatusBadge :value="item.status" />
          <strong class="inspection-count">{{ item.value }}</strong>
          <p class="inspection-hint">{{ item.hint }}</p>
          <p class="inspection-plan">{{ inspectionStatistics.handlingPlans[item.status] || '' }}</p>
        </div>
      </div>
    </section>

    <div class="split-grid">
      <section class="panel">
        <SectionHeader title="Upcoming Plans" description="Sorted by scheduled date" />
        <DataTable
          :columns="[
            { key: 'title', label: 'Plan' },
            { key: 'elevatorCode', label: 'Elevator' },
            { key: 'scheduledDate', label: 'Date' },
            { key: 'status', label: 'Status' },
          ]"
          :rows="upcomingPlans"
        >
          <template #status="{ row }">
            <StatusBadge :value="row.status" />
          </template>
        </DataTable>
      </section>

      <section class="panel">
        <SectionHeader title="Priority Faults" description="High priority repair queue" />
        <DataTable
          :columns="[
            { key: 'faultType', label: 'Type' },
            { key: 'elevatorCode', label: 'Elevator' },
            { key: 'priority', label: 'Priority' },
            { key: 'status', label: 'Status' },
          ]"
          :rows="urgentFaults"
        >
          <template #priority="{ row }">
            <StatusBadge :value="row.priority" />
          </template>
          <template #status="{ row }">
            <StatusBadge :value="row.status" />
          </template>
        </DataTable>
      </section>
    </div>
  </div>
</template>
