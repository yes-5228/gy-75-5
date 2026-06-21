<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { Activity, Building2, ClipboardCheck, FileClock, LayoutDashboard, Wrench } from 'lucide-vue-next'
import { catalogApi, maintenanceApi, repairApi } from './api/modules'
import AppShell from './components/AppShell.vue'
import DashboardView from './views/DashboardView.vue'
import ElevatorCatalogView from './views/ElevatorCatalogView.vue'
import FaultReportView from './views/FaultReportView.vue'
import InspectionView from './views/InspectionView.vue'
import MaintenancePlanView from './views/MaintenancePlanView.vue'
import RepairTrackingView from './views/RepairTrackingView.vue'

const activeView = ref('dashboard')
const loading = ref(false)
const error = ref('')
const inspectionSubmitting = ref(false)
const inspectionError = ref('')
const severeFaultInfo = ref(null)

const state = reactive({
  communities: [],
  elevators: [],
  plans: [],
  inspections: [],
  faults: [],
  tracking: [],
  statistics: {
    totalFaults: 0,
    openFaults: 0,
    completedFaults: 0,
    totalCost: 0,
    statusCounts: {},
    priorityCounts: {},
  },
  inspectionStatistics: {
    totalInspections: 0,
    normalCount: 0,
    slightAbnormalCount: 0,
    severeAbnormalCount: 0,
    resultCounts: {},
    handlingPlans: {},
  },
})

const tabs = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'catalog', label: 'Elevator Catalog', icon: Building2 },
  { id: 'plans', label: 'Maintenance Plans', icon: FileClock },
  { id: 'inspections', label: 'Inspections', icon: ClipboardCheck },
  { id: 'faults', label: 'Fault Reports', icon: Activity },
  { id: 'tracking', label: 'Repair Tracking', icon: Wrench },
]

const currentTitle = computed(() => tabs.find((tab) => tab.id === activeView.value)?.label || '')

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const [communities, elevators, plans, inspections, faults, tracking, statistics, inspectionStatistics] = await Promise.all([
      catalogApi.communities(),
      catalogApi.elevators(),
      maintenanceApi.plans(),
      maintenanceApi.inspections(),
      repairApi.faults(),
      repairApi.tracking(),
      repairApi.statistics(),
      maintenanceApi.inspectionStatistics(),
    ])
    state.communities = communities.items
    state.elevators = elevators.items
    state.plans = plans.items
    state.inspections = inspections.items
    state.faults = faults.items
    state.tracking = tracking.items
    state.statistics = statistics
    state.inspectionStatistics = inspectionStatistics
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function createPlan(payload) {
  await maintenanceApi.createPlan(payload)
  await loadAll()
}

async function updatePlan(id, payload) {
  await maintenanceApi.updatePlan(id, payload)
  await loadAll()
}

const inspectionViewRef = ref(null)

async function createInspection(payload) {
  inspectionSubmitting.value = true
  inspectionError.value = ''
  severeFaultInfo.value = null
  try {
    const result = await maintenanceApi.createInspection(payload)
    await loadAll()
    if (inspectionViewRef.value) {
      inspectionViewRef.value.resetForm()
    }
    if (result && result.createdFault) {
      severeFaultInfo.value = result.createdFault
    }
  } catch (err) {
    inspectionError.value = err.message || 'Failed to submit inspection record. Please try again.'
  } finally {
    inspectionSubmitting.value = false
  }
}

function closeSevereFaultDialog() {
  severeFaultInfo.value = null
}

function goToFaultReports() {
  severeFaultInfo.value = null
  activeView.value = 'faults'
}

async function createFault(payload) {
  await repairApi.createFault(payload)
  await loadAll()
}

async function createTracking(payload) {
  await repairApi.createTracking(payload)
  await loadAll()
}

onMounted(loadAll)
</script>

<template>
  <AppShell
    :tabs="tabs"
    :active-view="activeView"
    :title="currentTitle"
    :loading="loading"
    :error="error"
    @switch="activeView = $event"
    @refresh="loadAll"
  >
    <DashboardView
      v-if="activeView === 'dashboard'"
      :statistics="state.statistics"
      :inspection-statistics="state.inspectionStatistics"
      :plans="state.plans"
      :faults="state.faults"
      :elevators="state.elevators"
    />
    <ElevatorCatalogView
      v-else-if="activeView === 'catalog'"
      :elevators="state.elevators"
    />
    <MaintenancePlanView
      v-else-if="activeView === 'plans'"
      :plans="state.plans"
      :elevators="state.elevators"
      @create="createPlan"
      @update="updatePlan"
    />
    <InspectionView
      ref="inspectionViewRef"
      v-else-if="activeView === 'inspections'"
      :records="state.inspections"
      :elevators="state.elevators"
      :handling-plans="state.inspectionStatistics.handlingPlans"
      :submitting="inspectionSubmitting"
      :submit-error="inspectionError"
      :severe-fault-info="severeFaultInfo"
      @create="createInspection"
      @close-severe-dialog="closeSevereFaultDialog"
      @go-to-faults="goToFaultReports"
    />
    <FaultReportView
      v-else-if="activeView === 'faults'"
      :faults="state.faults"
      :elevators="state.elevators"
      @create="createFault"
    />
    <RepairTrackingView
      v-else
      :faults="state.faults"
      :logs="state.tracking"
      @create="createTracking"
    />
  </AppShell>
</template>
