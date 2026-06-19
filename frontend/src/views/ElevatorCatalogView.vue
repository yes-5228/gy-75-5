<script setup>
import { Building2 } from 'lucide-vue-next'
import DataTable from '../components/DataTable.vue'
import SectionHeader from '../components/SectionHeader.vue'
import StatusBadge from '../components/StatusBadge.vue'

defineProps({
  elevators: { type: Array, required: true },
})
</script>

<template>
  <div class="view-stack">
    <section class="panel">
      <SectionHeader title="Elevator Catalog" description="Elevator archive with latest inspection status" />
      <DataTable
        :columns="[
          { key: 'code', label: 'Elevator Code' },
          { key: 'communityName', label: 'Community' },
          { key: 'building', label: 'Building' },
          { key: 'unit', label: 'Unit' },
          { key: 'brand', label: 'Brand' },
          { key: 'status', label: 'Status' },
          { key: 'latestInspectionResult', label: 'Latest Inspection' },
          { key: 'latestInspectionAt', label: 'Inspection Date' },
          { key: 'inspectionHandlingPlan', label: 'Handling Plan' },
        ]"
        :rows="elevators"
      >
        <template #status="{ row }">
          <StatusBadge :value="row.status" />
        </template>
        <template #latestInspectionResult="{ row }">
          <StatusBadge v-if="row.latestInspectionResult" :value="row.latestInspectionResult" />
          <span v-else class="empty-text">No record</span>
        </template>
        <template #latestInspectionAt="{ row }">
          <span v-if="row.latestInspectionAt">{{ row.latestInspectionAt }}</span>
          <span v-else class="empty-text">-</span>
        </template>
        <template #inspectionHandlingPlan="{ row }">
          <span class="handling-plan-text">{{ row.inspectionHandlingPlan || '-' }}</span>
        </template>
      </DataTable>
    </section>
  </div>
</template>
