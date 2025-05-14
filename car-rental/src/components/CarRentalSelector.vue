<template>
  <section class="car-rental-selector">
    <div class="selector">
      <!-- 第一行：位置选择 -->
      <div class="row location-row">
        <div class="location-selection">
          <div class="location-title">取车地点</div>
          <div class="select-group">
            <div class="province-select">
              <n-select
                  v-model:value="selectedProvince"
                  :options="provinceOptions"
                  placeholder="选择省"
                  @update:value="handleProvinceChange"
              />
            </div>
            <div class="city-select">
              <n-select
                  v-model:value="selectedCity"
                  :options="cityOptions"
                  placeholder="选择市"
                  @update:value="handleCityChange"
                  :disabled="!selectedProvince"
              />
            </div>
            <div class="district-select">
              <n-select
                  v-model:value="selectedDistrict"
                  :options="districtOptions"
                  placeholder="选择区"
                  :disabled="!selectedCity"
              />
            </div>
            <div class="station-select">
              <n-select
                  v-model:value="selectedStation"
                  :options="stationOptions"
                  placeholder="选择取车网点"
                  :disabled="!selectedDistrict"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 添加还车地点选择 -->
      <div class="row location-row" v-if="isDifferentLocation">
        <div class="location-selection">
          <div class="location-title">还车地点</div>
          <div class="select-group">
            <div class="province-select">
              <n-select
                  v-model:value="returnProvince"
                  :options="provinceOptions"
                  placeholder="选择省"
                  @update:value="handleReturnProvinceChange"
              />
            </div>
            <div class="city-select">
              <n-select
                  v-model:value="returnCity"
                  :options="returnCityOptions"
                  placeholder="选择市"
                  @update:value="handleReturnCityChange"
                  :disabled="!returnProvince"
              />
            </div>
            <div class="district-select">
              <n-select
                  v-model:value="returnDistrict"
                  :options="returnDistrictOptions"
                  placeholder="选择区"
                  :disabled="!returnCity"
              />
            </div>
            <div class="station-select">
              <n-select
                  v-model:value="returnStation"
                  :options="stationOptions"
                  placeholder="选择还车网点"
                  :disabled="!returnDistrict"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 第二行：时间选择和操作 -->
      <div class="row time-row">
        <div class="time-group">
          <div class="time-label">取车时间：</div>
          <div class="time-container">
            <n-date-picker
                v-model:value="pickupDate"
                type="date"
                placeholder="选择取车日期"
                clearable
                :is-date-disabled="isDateDisabled"
            />
            <n-time-picker
                v-model:value="pickupTime"
                format="HH:mm"
                :minute-step="30"
                :minutes="allowedMinutes"
                placeholder="选择取车时间"
                clearable
                :is-time-disabled="isTimeDisabled"
            />
          </div>
        </div>
        <div class="time-group">
          <div class="time-label">还车时间：</div>
          <div class="time-container">
            <n-date-picker
                v-model:value="returnDate"
                type="date"
                placeholder="选择还车日期"
                clearable
                :disabled="!pickupDate"
                :is-date-disabled="isReturnDateDisabled"
            />
            <n-time-picker
                v-model:value="returnTime"
                format="HH:mm"
                :minute-step="30"
                :minutes="allowedMinutes"
                placeholder="选择还车时间"
                clearable
                :disabled="!returnDate"
                :is-time-disabled="isReturnTimeDisabled"
            />
          </div>
        </div>
        <div class="actions">
          <n-checkbox v-model:checked="isDifferentLocation">
            异地还车
          </n-checkbox>
          <button 
            class="rent-button" 
            @click="confirmRental" 
            :disabled="!isFormValid"
            :class="{ 'disabled': !isFormValid }">
            确认租车
          </button>
        </div>
      </div>
    </div>

    <!-- 弹窗组件 -->
    <n-modal
      v-model:show="showModal"
      preset="dialog"
      title="提示"
      positive-text="确认"
      negative-text="取消"
      :style="modalStyle"
      @positive-click="handleModalConfirm"
      @negative-click="handleModalCancel"
      style="width: 400px"
    >
      <template #header>
        <div class="modal-header">提示</div>
      </template>
      <div class="modal-content" v-html="modalMessage"></div>
    </n-modal>
  </section>
</template>

<script>
import { NDatePicker, NSelect, NTimePicker, NCheckbox, NModal } from 'naive-ui'

export default {
  name: "CarRentalSelector",
  components: {
    NDatePicker,
    NSelect,
    NTimePicker,
    NCheckbox,
    NModal
  },
  data() {
    return {
      selectedProvince: null,
      selectedCity: null,
      selectedDistrict: null,
      selectedStation: null,
      returnProvince: null,
      returnCity: null,
      returnDistrict: null,
      returnStation: null,
      pickupDate: null,
      pickupTime: null,
      returnDate: null,
      returnTime: null,
      isDifferentLocation: false,
      showModal: false,
      modalMessage: '',
      provinceOptions: [],
      cityOptions: [],
      districtOptions: [],
      returnCityOptions: [],
      returnDistrictOptions: [],
      stationOptions: [
        { label: '武林门店', value: 1, address: '杭州市西湖区武林路28号', business_hours: '09:00 - 18:00', phone: '0571-12345678' },
        { label: '黄龙店', value: 2, address: '杭州市西湖区黄龙路9号', business_hours: '08:00 - 17:00', phone: '0571-87654321' },
        { label: '西湖风景区店', value: 7, address: '杭州市西湖区龙井路32号', business_hours: '08:00 - 19:00', phone: '0571-67890123' }
      ],
      allowedMinutes: [0, 30]
    }
  },
  computed: {
    isFormValid() {
      const hasLocation = this.selectedProvince && this.selectedCity && 
                         this.selectedDistrict && this.selectedStation
      const hasReturnLocation = !this.isDifferentLocation || 
                               (this.returnProvince && this.returnCity && 
                                this.returnDistrict && this.returnStation)
      const hasPickupTime = this.pickupDate && this.pickupTime
      const hasReturnTime = this.returnDate && this.returnTime
      return hasLocation && hasReturnLocation && hasPickupTime && hasReturnTime && this.isTimeValid
    },
    isTimeValid() {
      if (!this.pickupDate || !this.pickupTime || !this.returnDate || !this.returnTime) {
        return false
      }

      const pickupDateTime = new Date(this.pickupDate)
      const pickupTime = new Date(this.pickupTime)
      pickupDateTime.setHours(pickupTime.getHours(), pickupTime.getMinutes())

      const returnDateTime = new Date(this.returnDate)
      const returnTime = new Date(this.returnTime)
      returnDateTime.setHours(returnTime.getHours(), returnTime.getMinutes())

      const now = new Date()
      
      return pickupDateTime > now && returnDateTime > pickupDateTime
    }
  },
  mounted() {
    this.fetchProvinces()
  },
  methods: {
    showModalMessage(message) {
      this.modalMessage = message
      this.showModal = true
    },

    handleModalConfirm() {
      this.showModal = false
      this.$router.push({
        name: 'showcase',
        query: {
          pickupStation: this.selectedStation,
          returnStation: this.isDifferentLocation ? this.returnStation : this.selectedStation,
          pickupTime: new Date(this.pickupDate).getTime() + new Date(this.pickupTime).getTime(),
          returnTime: new Date(this.returnDate).getTime() + new Date(this.returnTime).getTime()
        }
      })
    },

    handleModalCancel() {
      this.showModal = false
    },

    fetchProvinces() {
      fetch('http://localhost:5000/api/provinces')
          .then(response => response.json())
          .then(data => {
            this.provinceOptions = data.provinces
          })
          .catch(error => {
            console.error('获取省份数据失败:', error)
          })
    },

    fetchCities(provinceId) {
      fetch(`http://localhost:5000/api/cities?province_id=${provinceId}`)
          .then(response => response.json())
          .then(data => {
            this.cityOptions = data.cities
          })
          .catch(error => {
            console.error('获取城市数据失败:', error)
          })
    },

    fetchCountries(cityId) {
      fetch(`http://localhost:5000/api/countries?city_id=${cityId}`)
          .then(response => response.json())
          .then(data => {
            this.districtOptions = data.countries
          })
          .catch(error => {
            console.error('获取区域数据失败:', error)
          })
    },

    handleReturnProvinceChange(provinceValue) {
      this.returnCity = null
      this.returnDistrict = null
      this.returnStation = null
      fetch(`http://localhost:5000/api/cities?province_id=${provinceValue}`)
        .then(response => response.json())
        .then(data => {
          this.returnCityOptions = data.cities
        })
        .catch(error => {
          console.error('获取城市数据失败:', error)
        })
    },

    handleReturnCityChange(cityValue) {
      this.returnDistrict = null
      this.returnStation = null
      fetch(`http://localhost:5000/api/countries?city_id=${cityValue}`)
        .then(response => response.json())
        .then(data => {
          this.returnDistrictOptions = data.countries
        })
        .catch(error => {
          console.error('获取区域数据失败:', error)
        })
    },

    isDateDisabled(timestamp) {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      return timestamp < today.getTime()
    },

    isTimeDisabled(hour, minute) {
      if (!this.pickupDate) return true

      const selectedDate = new Date(this.pickupDate)
      const selectedTime = new Date(selectedDate)
      selectedTime.setHours(hour, minute, 0, 0)
      const now = new Date()
      
      if (selectedDate.getDate() === now.getDate() && 
          selectedDate.getMonth() === now.getMonth() && 
          selectedDate.getFullYear() === now.getFullYear()) {
        return selectedTime.getTime() <= now.getTime()  
      }
      
      return false
    },

    isReturnDateDisabled(timestamp) {
      if (!this.pickupDate) return true
      
      const selectedDate = new Date(timestamp)
      const pickupDate = new Date(this.pickupDate)
      const now = new Date()
      now.setHours(0, 0, 0, 0)

      return selectedDate.getTime() < now.getTime() || 
             selectedDate.getTime() < pickupDate.getTime()
    },

    isReturnTimeDisabled(hour, minute) {
      if (!this.returnDate) return true

      const returnDateTime = new Date(this.returnDate)
      returnDateTime.setHours(hour, minute, 0, 0)
      const now = new Date()

      if (returnDateTime.getTime() <= now.getTime()) {
        return true
      }

      if (this.pickupDate && this.pickupTime) {
        const pickupDateTime = new Date(this.pickupDate)
        const pickupTime = new Date(this.pickupTime)
        pickupDateTime.setHours(pickupTime.getHours(), pickupTime.getMinutes())
        return returnDateTime.getTime() <= pickupDateTime.getTime()
      }

      return false
    },

    handleProvinceChange(provinceValue) {
      this.selectedCity = null
      this.selectedDistrict = null
      this.selectedStation = null
      this.fetchCities(provinceValue)
    },

    handleCityChange(cityValue) {
      this.selectedDistrict = null
      this.selectedStation = null
      this.fetchCountries(cityValue)
    },

    confirmRental() {
      if (!this.isFormValid) {
        this.showModalMessage('请完整填写租车信息')
        return
      }

      const provinceName = this.provinceOptions.find(p => p.value === this.selectedProvince)?.label
      const cityName = this.cityOptions.find(city => city.value === this.selectedCity)?.label
      const districtName = this.districtOptions.find(district => district.value === this.selectedDistrict)?.label
      const stationName = this.stationOptions.find(station => station.value === this.selectedStation)?.label

      let returnLocationInfo = ''
      if (this.isDifferentLocation) {
        const returnProvinceName = this.provinceOptions.find(p => p.value === this.returnProvince)?.label
        const returnCityName = this.returnCityOptions.find(city => city.value === this.returnCity)?.label
        const returnDistrictName = this.returnDistrictOptions.find(district => district.value === this.returnDistrict)?.label
        const returnStationName = this.stationOptions.find(station => station.value === this.returnStation)?.label
        returnLocationInfo = `<br>还车位置: ${returnProvinceName} ${returnCityName} ${returnDistrictName} ${returnStationName}`
      }
      
      const pickupDateTime = new Date(this.pickupDate)
      const pickupTime = new Date(this.pickupTime)
      pickupDateTime.setHours(pickupTime.getHours(), pickupTime.getMinutes())
      
      const returnDateTime = new Date(this.returnDate)
      const returnTime = new Date(this.returnTime)
      returnDateTime.setHours(returnTime.getHours(), returnTime.getMinutes())

      this.showModalMessage(
        `租车信息:<br>` +
        `取车位置: ${provinceName} ${cityName} ${districtName} ${stationName}` +
        returnLocationInfo + '<br>' +
        `取车时间: ${pickupDateTime.toLocaleString()}<br>` +
        `还车时间: ${returnDateTime.toLocaleString()}<br>` +
        `是否异地还车: ${this.isDifferentLocation ? '是' : '否'}`
      )
    }
  },
  watch: {
    isDifferentLocation(newVal) {
      if (!newVal) {
        // 取消异地还车时清空还车地点数据
        this.returnProvince = null
        this.returnCity = null
        this.returnDistrict = null
        this.returnStation = null
        this.returnCityOptions = []
        this.returnDistrictOptions = []
      }
    },
    pickupTime: {
      handler(newVal) {
        if (!newVal || !this.pickupDate) return
        
        const selectedDateTime = new Date(this.pickupDate)
        const selectedTime = new Date(newVal)
        selectedDateTime.setHours(selectedTime.getHours(), selectedTime.getMinutes())
        
        const now = new Date()
        if (selectedDateTime.getTime() <= now.getTime()) {
          this.$nextTick(() => {
            this.pickupTime = null
            this.showModalMessage('取车时间不能早于当前时间')
          })
          return
        }

        if (this.returnDate && this.returnTime) {
          const returnDateTime = new Date(this.returnDate)
          const returnTime = new Date(this.returnTime)
          returnDateTime.setHours(returnTime.getHours(), returnTime.getMinutes())

          if (returnDateTime.getTime() <= selectedDateTime.getTime()) {
            this.returnDate = null
            this.returnTime = null
            this.showModalMessage('还车时间不能早于取车时间，请重新选择还车时间')
          }
        }
      }
    },
    
    pickupDate: {
      handler(newVal) {
        if (!newVal) {
          this.pickupTime = null
          return
        }

        const selectedDate = new Date(newVal)
        const now = new Date()
        now.setHours(0, 0, 0, 0)
        
        if (selectedDate.getTime() < now.getTime()) {
          this.$nextTick(() => {
            this.pickupDate = null
            this.showModalMessage('取车日期不能早于当前日期')
          })
          return
        }
        
        this.pickupTime = null
        
        if (this.returnDate) {
          const returnDate = new Date(this.returnDate)
          if (returnDate.getTime() < selectedDate.getTime()) {
            this.returnDate = null
            this.returnTime = null
            this.showModalMessage('还车日期不能早于取车日期，请重新选择还车时间')
          }
        }
      }
    },

    returnTime: {
      handler(newVal) {
        if (!newVal || !this.returnDate || !this.pickupDate || !this.pickupTime) return

        const returnDateTime = new Date(this.returnDate)
        const returnTime = new Date(newVal)
        returnDateTime.setHours(returnTime.getHours(), returnTime.getMinutes())

        const pickupDateTime = new Date(this.pickupDate)
        const pickupTime = new Date(this.pickupTime)
        pickupDateTime.setHours(pickupTime.getHours(), pickupTime.getMinutes())
        
        const now = new Date()

        if (returnDateTime.getTime() <= now.getTime()) {
          this.$nextTick(() => {
            this.returnTime = null
            this.showModalMessage('还车时间不能早于当前时间')
          })
          return
        }

        if (returnDateTime.getTime() <= pickupDateTime.getTime()) {
          this.$nextTick(() => {
            this.returnTime = null
            this.showModalMessage('还车时间不能早于取车时间')
          })
        }
      }
    },

    returnDate: {
      handler(newVal) {
        if (!newVal) return

        const returnDate = new Date(newVal)
        const now = new Date()
        now.setHours(0, 0, 0, 0)

        if (returnDate.getTime() < now.getTime()) {
          this.$nextTick(() => {
            this.returnDate = null
            this.showModalMessage('还车日期不能早于当前日期')
          })
          return
        }

        if (this.pickupDate) {
          const pickupDate = new Date(this.pickupDate)
          if (returnDate.getTime() < pickupDate.getTime()) {
            this.$nextTick(() => {
              this.returnDate = null
              this.showModalMessage('还车日期不能早于取车日期')
            })
          }
        }
      }
    }
  }
}
</script>

<style scoped>
.car-rental-selector {
  display: flex;
  justify-content: center;
  margin: 20px 0;
  width: 80%;
}

.selector {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  max-width: 1200px;
}

.row {
  display: flex;
  width: 100%;
}

.location-selection {
  flex: 1;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.location-title {
  font-weight: 500;
  margin-bottom: 10px;
}

.select-group {
  display: flex;
  gap: 10px;
}

.province-select,
.city-select,
.district-select,
.station-select {
  flex: 1;
}

.time-row {
  display: flex;
  gap: 20px;
  align-items: center;
}

.time-group {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 10px;
}

.time-label {
  white-space: nowrap;
  font-weight: 500;
}

.time-container {
  display: flex;
  gap: 10px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: nowrap; /* Prevent wrapping */

  justify-content: flex-end;
}

:deep(.n-select),
:deep(.n-date-picker),
:deep(.n-time-picker) {
  width: 100%;
}

.different-location-checkbox {
  white-space: nowrap;
}

.rent-button {
  height: 42px;
  padding: 0 20px;
  background-color: #ffbb00;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s, opacity 0.3s;
  white-space: nowrap;
  flex-shrink: 0;
}

.rent-button:hover:not(.disabled) {
  background-color: #bb5500;
}

.rent-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #ffbb00;
}

:deep(.n-modal) {
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.n-modal-body-wrapper) {
  white-space: pre-line;
}

:deep(.n-button--primary-type) {
  background-color: #ffbb00 !important;
  border-color: #ffbb00 !important;
}

:deep(.n-button--primary-type:hover) {
  background-color: #bb5500 !important;
  border-color: #bb5500 !important;
}

:deep(.n-dialog__title) {
  color: #ffbb00 !important;
}

.modal-header {
  color: #000000;
  font-size: 18px;
  font-weight: 500;
}

.modal-content {
  padding: 20px 0;
  line-height: 1.6;
}

:deep(.n-modal-mask) {
  background-color: rgba(0, 0, 0, 0.5) !important;
}

:deep(.n-button:hover) {
  color: #fff !important;
}

:deep(.n-dialog__content) {
  color: #333 !important;
}
</style>