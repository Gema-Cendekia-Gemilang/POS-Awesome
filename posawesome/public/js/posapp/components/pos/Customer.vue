<template>
  <div>
    <v-autocomplete
      dense
      clearable
      auto-select-first
      outlined
      color="primary"
      :label="frappe._('Pilih Customer & Kendaraan')"
      v-model="selectedVehicle"
      :items="customerVehicles"
      item-text="display_text"
      item-value="vehicle_name"
      background-color="white"
      :no-data-text="__('Customer atau Kendaraan tidak ditemukan')"
      hide-details
      :filter="customFilter"
      :disabled="readonly"
      append-icon="mdi-plus"
      @click:append="new_customer"
      prepend-inner-icon="mdi-account-edit"
      @click:prepend-inner="edit_customer"
    >
      <template v-slot:item="{ item }">
        <v-list-item-content>
          <v-list-item-title class="primary--text subtitle-1">
            {{ item.customer_name }} : {{ item.license_plate }}
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ item.brand }} {{ item.model }}
          </v-list-item-subtitle>
        </v-list-item-content>
      </template>
    </v-autocomplete>

    <div v-if="selectedVehicleData">
      <p><strong>Customer:</strong> {{ selectedVehicleData.customer_name }}</p>
      <p><strong>Kendaraan:</strong> {{ selectedVehicleData.license_plate }} ({{ selectedVehicleData.brand }} {{ selectedVehicleData.model }})</p>
      <p><strong>Nomor HP:</strong> {{ selectedVehicleData.mobile_no || 'Tidak tersedia' }}</p>
    </div>

    <div class="mb-8">
      <UpdateCustomer></UpdateCustomer>
    </div>
  </div>
</template>

<script>
import { evntBus } from '../../bus';
import UpdateCustomer from './UpdateCustomer.vue';

export default {
  components: {
    UpdateCustomer,
  },

  data() {
    return {
      pos_profile: '',
      customers: [],
      customerVehicles: [],
      selectedVehicle: '',
      readonly: false,
      customer_info: {}, // Simpan data pelanggan dari API
    };
  },

  computed: {
     selectedVehicleData() {
      return this.customer_info.vehicles 
        ? this.customer_info.vehicles.find(vehicle => vehicle.vehicle_name === this.selectedVehicle) 
        : null;
    },
  },

  methods: {
    get_customer_names() {
      if (this.customers.length > 0) return;

      frappe.call({
        method: 'reparo.api.customer.get_customer_names',
        args: { pos_profile: this.pos_profile.pos_profile },
        callback: (r) => {
          console.log("Response API:", r.message);
          if (r.message) {
            this.customers = r.message;
            this.processCustomerData();
          } else {
            console.error("Tidak ada data pelanggan ditemukan.");
          }
        },
        error: (err) => {
          console.error("Error API:", err);
        }
      });
    },

    processCustomerData() {
      console.log("Data pelanggan sebelum diproses:", this.customers);

      if (!Array.isArray(this.customers)) {
        console.error("Data pelanggan tidak valid:", this.customers);
        this.customerVehicles = [];
        return;
      }

      this.customerVehicles = this.customers.flatMap(customer => {
        if (!customer.vehicles || !Array.isArray(customer.vehicles)) {
          console.warn("Data kendaraan kosong atau tidak valid untuk customer:", customer);
          return [];
        }

        return customer.vehicles.map(vehicle => ({
          customer_name: customer.customer_name || 'Tidak diketahui',
          vehicle_name: vehicle.name || 'tidak diketahui',
          mobile_no: customer.mobile_no || 'Tidak tersedia',
          license_plate: vehicle.license_plate || 'Tidak diketahui',
          brand: vehicle.brand || 'Tidak diketahui',
          model: vehicle.model || 'Tidak diketahui',
          display_text: `${customer.customer_name || 'Tidak diketahui'} : ${vehicle.license_plate || 'Tidak diketahui'}`
        }));
      });

      console.log("Data customerVehicles setelah diproses:", this.customerVehicles);
    },

    new_customer() {
      evntBus.$emit('open_update_customer', null);
    },

    edit_customer() {
      if (!this.selectedVehicleData) {
        console.warn("Tidak ada data kendaraan yang dipilih untuk diedit.");
        return;
      }
      evntBus.$emit('open_update_customer', this.selectedVehicleData);
    },

    customFilter(item, queryText) {
      const searchText = queryText.toLowerCase();
      return [
        item.customer_name?.toLowerCase(),
        item.license_plate?.toLowerCase(),
        item.brand?.toLowerCase(),
        item.model?.toLowerCase()
      ].some(text => text?.includes(searchText));
    },
  },

  created() {
    this.$nextTick(() => {
      evntBus.$on('register_pos_profile', (pos_profile) => {
        this.pos_profile = pos_profile;
        console.log("Profil POS Diterima:", pos_profile);
        this.get_customer_names();
      });

      evntBus.$on('set_customer', (customer) => {
        console.log("Event set_customer diterima:", customer);

        if (!customer || !customer.name) {
          console.warn("Customer tidak valid atau tidak memiliki name:", customer);
          return;
        }

        const foundVehicle = this.customerVehicles.find(v => v.vehicle_name === customer.vehicle_name);
        if (!foundVehicle) {
          console.warn(`Kendaraan dengan ID ${customer.vehicle_name} tidak ditemukan dalam customerVehicles`, this.customerVehicles);
        }

        this.selectedVehicle = customer.vehicle_name;
      });
    });
  },

  watch: {
    selectedVehicle(newValue) {
      console.log("Kendaraan yang dipilih:", newValue);
      const foundVehicle = this.customerVehicles.find(v => v.vehicle_name === newValue);
      if (!foundVehicle) {
        console.warn("Data kendaraan tidak ditemukan untuk ID:", newValue, this.customerVehicles);
      }
      evntBus.$emit('update_customer', foundVehicle || null);
    }
  }
};
</script>
