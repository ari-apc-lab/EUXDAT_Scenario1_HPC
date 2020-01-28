
/*eslint no-unused-vars: "error"*/
<template >

  <v-container fluid grid-list-md fill-height style="padding: 0px;">
    <v-layout row wrap style="font-family: Roboto,Helvetica,Arial,sans-serif !important;">

      <div class="flex xs3 offset-xs9" style="padding: 0px;">
          <v-toolbar class="green" tabs>
            <v-toolbar-title>
              <img style="width: 60px;" src="../assets/logo_1-1.png" alt="">
            </v-toolbar-title>
            <v-spacer></v-spacer>
            <span style="color:#27304c">
              <v-icon>person</v-icon> {{user.name}}
            </span>
            <v-btn icon title="Exit app" @click="logout()">
              <v-icon color="#27304c">exit_to_app</v-icon>
            </v-btn>
          </v-toolbar>

          <v-flex xs12 style="text-align: center">
            <v-btn small dark color="#5cb860" :loading="isLoading" class="flex xs12" @click="getPolygons(map)" title="Display polygons">
              <v-icon>fullscreen</v-icon>
              Display field boundaries
            </v-btn>
          </v-flex>
          <!--
          <v-switch
            v-model="switchElevation"
            :label="`Switch 1: ${switchElevation.toString()}`"
          ></v-switch>
          -->

          <v-flex xs12 mr-2>
            <v-card>

              <v-list three-line style="padding: 0px;">
                <template >
                  <v-subheader>
                    Elevation
                    <v-spacer></v-spacer>
                    <v-btn v-if="isSelected" icon title="Download elevation image" @click="downloadImage('elevation')">
                      <v-icon color="#4caf50">archive</v-icon>
                    </v-btn>
                  </v-subheader>

                  <v-divider></v-divider>

                  <v-list-tile v-if="isSelected">

                    <v-list-tile-content>
                      <v-list-tile-sub-title > <strong>Mean:</strong> {{selectedPolygon.elevation.mean}}</v-list-tile-sub-title >
                      <v-list-tile-sub-title > <strong>Max:</strong> {{selectedPolygon.elevation.max}}</v-list-tile-sub-title >
                        <v-list-tile-sub-title > <strong>Min:</strong> {{selectedPolygon.elevation.min}}</v-list-tile-sub-title >
                    </v-list-tile-content>
                  </v-list-tile>
                </template>
              </v-list>

              <v-list three-line style="padding: 0px;">
                <template >
                  <v-subheader>
                    Slope
                    <v-spacer></v-spacer>
                    <v-btn v-if="isSelected" icon title="Download slope image" @click="downloadImage('slope')">
                      <v-icon color="#4caf50">archive</v-icon>
                    </v-btn>
                  </v-subheader>

                  <v-divider></v-divider>

                  <v-list-tile v-if="isSelected">

                    <v-list-tile-content>
                      <v-list-tile-sub-title > <strong>Mean:</strong> {{selectedPolygon.slope.mean}}</v-list-tile-sub-title >
                      <v-list-tile-sub-title > <strong>Max:</strong> {{selectedPolygon.slope.max}}</v-list-tile-sub-title >
                        <v-list-tile-sub-title > <strong>Min:</strong> {{selectedPolygon.slope.min}}</v-list-tile-sub-title >
                    </v-list-tile-content>
                  </v-list-tile>
                </template>
              </v-list>

              <v-list three-line style="padding: 0px;">
                <template >
                  <v-subheader>
                    Azimuth
                    <v-spacer></v-spacer>
                    <v-btn v-if="isSelected" icon title="Download azimuth image" @click="downloadImage('azimuth')">
                      <v-icon color="#4caf50">archive</v-icon>
                    </v-btn>
                  </v-subheader>

                  <v-divider></v-divider>

                  <v-list-tile v-if="isSelected">

                    <v-list-tile-content>
                      <v-list-tile-sub-title > <strong>Mean:</strong> {{selectedPolygon.azimuth.mean}}</v-list-tile-sub-title >
                      <v-list-tile-sub-title > <strong>Max:</strong> {{selectedPolygon.azimuth.max}}</v-list-tile-sub-title >
                        <v-list-tile-sub-title > <strong>Min:</strong> {{selectedPolygon.azimuth.min}}</v-list-tile-sub-title >
                    </v-list-tile-content>
                  </v-list-tile>
                </template>
              </v-list>
              <v-list three-line style="padding: 0px;">
                <template >
                  <v-subheader>
                    Topographic wetness index
                    <v-spacer></v-spacer>
                    <v-btn v-if="isSelected" icon title="Download TWI image" @click="downloadImage('twi')">
                      <v-icon color="#4caf50">archive</v-icon>
                    </v-btn>
                  </v-subheader>

                  <v-divider></v-divider>

                  <v-list-tile v-if="isSelected">

                    <v-list-tile-content>
                      <v-list-tile-sub-title > <strong>Mean:</strong> {{selectedPolygon.twi.mean}}</v-list-tile-sub-title >
                      <v-list-tile-sub-title > <strong>Max:</strong> {{selectedPolygon.twi.max}}</v-list-tile-sub-title >
                        <v-list-tile-sub-title > <strong>Min:</strong> {{selectedPolygon.twi.min}}</v-list-tile-sub-title >
                    </v-list-tile-content>
                  </v-list-tile>
                </template>
              </v-list>


            </v-card>
          </v-flex>


        </div>
        <div id="map" class="flex xs9" style="position: fixed; height: 100%; width: 100%; padding: 0px; margin: 0px;">
          <div class="flex xs3" style="left: 10px; bottom: 10px; position: absolute; z-index: 10; " >
            <v-alert :value="isAlert" type="success" transition="scale-transition">
               Not polygons found, please zoom in and try again!
            </v-alert>
          </div>
          <div class="flex xs3" style="left: 10px; bottom: 10px; position: absolute; z-index: 10; " >
            <v-alert :value="isErrAlert" type="error" transition="scale-transition">
              {{errorMsg}}
            </v-alert>
          </div>

        </div>
    </v-layout>
  </v-container>

</template>

<script>

import Map from 'ol/Map.js';
import View from 'ol/View.js';
import {Tile as TileLayer, Vector as VectorLayer} from 'ol/layer.js';
import TileWMS from 'ol/source/TileWMS.js';
import GeoJSON from 'ol/format/GeoJSON.js';
import {Vector as VectorSource} from 'ol/source.js'
import {Select} from 'ol/interaction.js';
import {Fill, Stroke, Style} from 'ol/style.js';
import moment from 'moment';

export default {
  data: () => ({
    currentUser: {},
    map: {},
    mapExtent: [],
    selectedPolygon: {
      "elevation": {
        "min": "",
        "max": "",
        "mean": ""
      },
      "slope": {
        "min": "",
        "max": "",
        "mean": ""
      },
      "azimuth": {
        "min": "",
        "max": "",
        "mean": ""
      },
      "twi": {
        "min": "",
        "max": "",
        "mean": ""
      }
    },
    polygonID: "",
    polygonNut: "",
    switchElevation: true,
    isSelected: false,
    isAlert: false,
    isLoading: false,
    isErrAlert: false,
    errorMsg: ""
  }),
  watch: {
    /*
    switchElevation(val){
      this.showLayer('ele')
    }
    */
  },
  methods: {
    initMap() {
      var self = this;
      var defaultStyle = new Style({
        stroke: new Stroke({
          color: '#3994bd',
          width: 2
        }),
        fill: new Fill({
          color: 'rgba(0, 0, 0, 0)'
        })
      });
      var selectedStyle = [
        new Style({
          stroke: new Stroke({
            color: 'red',
            width: 3
          }),
          fill: new Fill({
            color: 'rgba(0, 0, 0, 0)'
          })
        })
      ];
      var drawLayer = new VectorLayer({
        source: new VectorSource(),
        name: 'userPolygonsLayer',
        style: defaultStyle
      });
      drawLayer.setZIndex(99)

     var myMap = new Map({
        target: 'map',

        layers: [
          drawLayer
        ],
        view: new View({
          projection: 'EPSG:3857',
          center: [1879819,6192339],
          zoom: 13
        })
      });

      this.mapExtent = myMap.getView().calculateExtent();

      var baseLayer = new TileLayer({
        source: new TileWMS({
          url: 	'http://gis.lesprojekt.cz/cgi-bin/mapserv?',
          params: {
            'map': '/home/dima/maps/olu/european_openlandusemap.map',
            'SERVICE': 'WMS',
            'VERSION': '1.3.0',
            'REQUEST': 'GetMap',
            'LAYERS': 'olu_poskladany',
            'CRS': '3857',
            'BBOX': this.mapExtent[0].toString().concat(',', this.mapExtent[1].toString(),
              ',', this.mapExtent[2].toString(), ',', this.mapExtent[3].toString()),
            'HEIGHT': '200',
            'WIDTH': '200',
            'FORMAT': 'image/png'
            },
        })
      });
      myMap.addLayer(baseLayer);

      this.interactionSelect = new Select();
      myMap.addInteraction(this.interactionSelect);

      this.interactionSelect.on('select', function(e) {
        self.polygonID = e.selected[0].get('id');
        self.polygonNut = e.selected[0].get('nuts_id');

        e.selected[0].setStyle(selectedStyle);
        if(e.deselected[0]){
          e.deselected[0].setStyle(defaultStyle);
        }
        self.getPolygonInfo(self.polygonID);
      });

      this.map = myMap;
    },//initMap
    getPolygons(map){

      this.isLoading = true;
      this.mapExtent = map.getView().calculateExtent();
      var ext = map.getView().calculateExtent()
      var url = 'https://olu-api.test.euxdat.eu/get_fields_geometry?bbox=' +
      ext[0] + "," + ext[1] + "," + ext[2] + "," + ext[3];

      var self = this;
      this.$http.get(url).then(response => {

          if(response.body.features.length === 0){
            self.showAlertFn();
          }else{
            self.getLayerFromMapByName(self.map, 'userPolygonsLayer').getSource().clear();
            self.getLayerFromMapByName(self.map, 'userPolygonsLayer').getSource()
              .addFeatures((new GeoJSON()).readFeatures(response.body));
              self.isLoading = false;
          }
      }, response => {
        self.isLoading = false;
        self.showErrAlertFn(response);
      });

    },//getPolygons
    getPolygonInfo(id){
      var url = 'https://olu-api.test.euxdat.eu/get_field_statistics?id=' + id + '&onfly=true'
      this.$http.get(url).then(response => {
          this.isSelected = true;
          this.selectedPolygon = response.body;
        }, response => {
          this.showErrAlertFn(response);
      });
    },//getPolygonInfo
    downloadImage(type){
      window.open('https://olu-api.test.euxdat.eu/get_field_raster?id=' +
      this.polygonID + '&onfly=true&output=image&kind=' + type);
    },//downloadImage
    /*
    showLayer(type){

      if(this.switchElevation){
      }


      //http://gis.lesprojekt.cz/cgi-bin/mapserv?map=/home/dima/maps/olu/european_openlandusemap.map&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&MUNICIPALITY=AT30810&ID=9993554&LAYERS=olu_by_id&CRS=EPSG:3857&BBOX=1876007,6195466,1877910,6197175&FORMAT=image/png&WIDTH=200&HEIGHT=200
      //http://gis.lesprojekt.cz/cgi-bin/mapserv?map=/home/dima/maps/olu/european_openlandusemap.map&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities
      console.log(this.mapExtent[1].toString().concat(',', this.mapExtent[0].toString(),
            ',', this.mapExtent[3].toString(), ',', this.mapExtent[2].toString()))

        var layer = new TileLayer({
          source: new TileWMS({
            url: 	'http://gis.lesprojekt.cz/cgi-bin/mapserv?',
            params: {
              'map': '/home/dima/maps/olu/european_openlandusemap.map',
              'SERVICE': 'WMS',
              'VERSION': '1.3.0',
              'REQUEST': 'GetMap',
              'MUNICIPALITY': this.polygonNut,
              'ID': this.polygonID,
              'LAYERS': 'olu_by_id',
              'CRS': '3857',
              'BBOX': this.mapExtent[0].toString().concat(',', this.mapExtent[1].toString(),
                ',', this.mapExtent[2].toString(), ',', this.mapExtent[3].toString()),
              'HEIGHT': '200',
              'WIDTH': '200',
              'FORMAT': 'image/png'
              },
            })
          })
          this.map.addLayer(layer);

    },//showLayer
    */
    showAlertFn(){
      this.isAlert = true;
      var self = this;
      setTimeout(function(){ self.isAlert = false; }, 3000);
    },//showAlertFn
    showErrAlertFn(response){
      this.isErrAlert = true;
      this.errorMsg = response;
      var self = this;
      setTimeout(function(){ self.isErrAlert = false; }, 3000);
    },//showAlertFn
    getLayerFromMapByName(map, name){
      var layer;
      map.getLayers().forEach(function(lyr) {
        if(lyr.get('name') === name){
          layer = lyr;
        }
      });
      return layer;
    },//getLayerFromMapByName
    logout: function(){
      this.$keycloak.logoutFn();
    },//logout
  },
  mounted: function(){
    this.initMap();
  },
  created(){
    var user = JSON.parse(window.atob(this.$keycloak.token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
    this.user = user;
  },
  filters: {
    truncate: function(value) {
      if(value != undefined){
        value = value.toString().substring(0, 8);
      }
      return value
    },
    formatDate: function(value) {
      if (value) {
        return moment(String(value)).format('MM/DD/YYYY hh:mm')
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
