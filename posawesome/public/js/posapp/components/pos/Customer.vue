<template>
  <div>
    <v-autocomplete
      :key="autocompleteKey"
      dense
      clearable
      auto-select-first
      outlined
      color="primary"
      :label="frappe._('Customer')"
      v-model="selectedCustomer"
      :items="processedCustomers"
      item-text="display_name"
      item-value="unique_key"  
      background-color="white"
      :no-data-text="__('Customer not found')"
      hide-details
      :filter="customFilter"
      :disabled="readonly"
      append-icon="mdi-account-plus"
      @click:append="new_customer"
      prepend-inner-icon="mdi-car-multiple"
      @click:prepend-inner="edit_customer"
    >
      <template v-slot:item="{ item }">
        <v-list-item-content>
          <v-list-item-title class="primary--text subtitle-1">
            {{ item.display_name || 'NO DISPLAY NAME' }}
          </v-list-item-title>
          <v-list-item-subtitle v-if="item.license_plate">
            License Plate: {{ item.license_plate }}
          </v-list-item-subtitle>
          <v-list-item-subtitle v-if="item.mobile_no">
            Mobile No: {{ item.mobile_no }}
          </v-list-item-subtitle>
        </v-list-item-content>
      </template>
    </v-autocomplete>
    <div class="mb-8">
      <UpdateCustomer />
    </div>
  </div>
</template>

<script>
import { evntBus } from "../../bus";
import UpdateCustomer from "./UpdateCustomer.vue";

export default {
  data() {
    return {
      pos_profile: "",
      customers: [],
      selectedCustomer: "", // Menyimpan customer_id saja
      autocompleteKey: 0,
      readonly: false,
      customer_info: {},
    };
  },

  components: {
    UpdateCustomer,
  },

  computed: {
    processedCustomers() {
      let processed = [];
      console.log("Data Customers:", this.customers);

      this.customers.forEach((customer) => {
        if (customer.vehicles && customer.vehicles.length > 0) {
          customer.vehicles.forEach((vehicle) => {
            processed.push({
              customer_id: customer.name, // Hanya simpan customer.name
              customer_name: customer.customer_name,
              display_name: `${customer.customer_name} : ${vehicle.license_plate}`,
              license_plate: vehicle.license_plate,
              mobile_no: customer.mobile_no || "N/A",
              unique_key: `${customer.name}_${vehicle.license_plate}`, // Buat kombinasi unik
            });
          });
        } else {
          processed.push({
            customer_id: customer.name, // Hanya simpan customer.name
            customer_name: customer.customer_name,
            display_name: customer.customer_name,
            license_plate: null,
            mobile_no: customer.mobile_no || "N/A",
            unique_key: `${customer.name}_no_license`, // Unik meskipun tanpa kendaraan
          });
        }
      });

      console.log("Processed Customers:", processed);
      return processed;
    },
  },

  methods: {
    get_customer_names() {
      if (this.customers.length > 0) return;

      if (this.pos_profile.posa_local_storage && localStorage.customer_storage) {
        try {
          this.customers = JSON.parse(localStorage.getItem("customer_storage"));
        } catch (e) {
          console.error("Error parsing customer_storage:", e);
        }
      }

      frappe.call({
        method: "reparo.api.customer.get_customer_names",
        args: {
          pos_profile: this.pos_profile.pos_profile,
        },
        callback: (r) => {
          console.log("API Response:", r.message);
          if (r.message && Array.isArray(r.message)) {
            this.$set(this, "customers", [...r.message]); // Paksa Vue mengenali perubahan
            if (this.pos_profile.posa_local_storage) {
              localStorage.setItem("customer_storage", JSON.stringify(r.message));
            }
          } else {
            console.error("Invalid response format:", r);
          }
        },
      });
    },

    new_customer() {
      evntBus.$emit("open_update_customer", null);
      this.$nextTick(() => {
        this.$set(this, "selectedCustomer", ""); 
        this.autocompleteKey++; 
      });
    },

    edit_customer() {
      evntBus.$emit("open_update_customer", this.customer_info);
      this.$nextTick(() => {
        this.$set(this, "selectedCustomer", ""); 
        this.autocompleteKey++; 
      });
    },

    customFilter(item, queryText) {
      if (!queryText) return true;
      const searchText = queryText.toLowerCase();
      return (
        item.customer_name.toLowerCase().includes(searchText) ||
        (item.license_plate && item.license_plate.toLowerCase().includes(searchText)) ||
        (item.mobile_no && item.mobile_no.toLowerCase().includes(searchText))
      );
    },
  },

  created: function () {
    this.$nextTick(function () {
      evntBus.$on('register_pos_profile', (pos_profile) => {
        this.pos_profile = pos_profile;
        this.get_customer_names();
      });
      evntBus.$on('payments_register_pos_profile', (pos_profile) => {
        this.pos_profile = pos_profile;
        this.get_customer_names();
      });
      evntBus.$on("set_customer", (customer) => {
        const selected = this.processedCustomers.find(c => c.customer_id === customer);
        if (selected) {
          this.selectedCustomer = selected.unique_key;
        }
      });
      evntBus.$on("add_customer_to_list", (customer) => {
        this.customers.push(customer);
      });
      evntBus.$on("set_customer_readonly", (value) => {
        this.readonly = value;
      });
      evntBus.$on("set_customer_info_to_edit", (data) => {
        this.customer_info = data;
      });
      evntBus.$on("fetch_customer_details", () => {
        this.get_customer_names();
      });
      evntBus.$on("customer_updated", () => {
        this.$nextTick(() => {
          this.selectedCustomer = ""; // Reset setelah update data customer
        });
      });
    });
  },

  watch: {
    selectedCustomer(newVal) {
      if (!newVal) return;

      const selectedCustomerObj = this.processedCustomers.find(
        (c) => c.unique_key === newVal
      );

      if (selectedCustomerObj) {
        this.customer = selectedCustomerObj.customer_name;
        evntBus.$emit("update_customer", this.customer);
        this.selectedCustomer = ""; // Reset otomatis setelah update event
      } else {
        this.selectedCustomer = ""; // Reset jika tidak ditemukan
      }
    },
  },
};
</script>
