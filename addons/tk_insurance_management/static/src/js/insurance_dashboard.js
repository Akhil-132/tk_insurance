odoo.define('tk_insurance_management.InsuranceDashboard', function (require) {
    'use strict';
    const AbstractAction = require('web.AbstractAction');
    const ajax = require('web.ajax');
    const core = require('web.core');
    const rpc = require('web.rpc');
    const session = require('web.session')
    const web_client = require('web.web_client');
    const _t = core._t;
    const QWeb = core.qweb;

    const ActionMenu = AbstractAction.extend({
        template: 'InsuranceDashboard',
        events: {
            'click .insurance-category': 'view_insurance_category',
            'click .total-insurance': 'view_total_insurance',
            'click .running-insurance': 'view_running_insurance',
            'click .expired-insurance': 'view_expired_insurance',
            'click .total-claim': 'view_total_claim',
            'click .submit-claim': 'view_submit_claim',
            'click .approved-claim': 'view_approved_claim',
            'click .not-approved-claim': 'view_not_approved_claim',
            'click .res-partner-agent': 'view_res_partner_agent',

        },
        renderElement: function (ev) {
            const self = this;
            $.when(this._super())
                .then(function (ev) {
                    rpc.query({
                        model: "insurance.dashboard",
                        method: "get_insurance_dashboard",
                    }).then(function (result) {
                        $('#insurance_category').empty().append(result['insurance_category']);
                        $('#total_insurance').empty().append(result['total_insurance']);
                        $('#running_insurance').empty().append(result['running_insurance']);
                        $('#expired_insurance').empty().append(result['expired_insurance']);
                        $('#total_claim').empty().append(result['total_claim']);
                        $('#submit_claim').empty().append(result['submit_claim']);
                        $('#approved_claim').empty().append(result['approved_claim']);
                        $('#not_approved_claim').empty().append(result['not_approved_claim']);
                        $('#res_partner_agent').empty().append(result['res_partner_agent']);
                        self.claimApprovedNotApproved(result['total_claim_count_graph']);
                        self.insuranceStateCondition(result['insurance_state_graph']);
                        self.insuranceTopAgent(result['top_agents']);
                        self.genderCount(result['gender_count']);
                    });
                });
        },
        view_insurance_category : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Insurance Category'),
                type: 'ir.actions.act_window',
                res_model: 'insurance.category',
                views: [[false, 'list'], [false, 'form']],
                target: 'current'
            });
        },
         view_total_insurance : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Total Insurances'),
                type: 'ir.actions.act_window',
                res_model: 'insurance.information',
                views: [[false, 'list'], [false, 'form']],
                target: 'current'
            });
        },
        view_running_insurance: function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Running Insurances'),
                type: 'ir.actions.act_window',
                domain: [['state', '=', 'running']],
                res_model: 'insurance.information',
                views: [[false, 'list'], [false, 'form']],
                target: 'current'
            });
        },
        view_expired_insurance: function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Expired Insurances'),
                type: 'ir.actions.act_window',
                domain: [['state', '=', 'expired']],
                res_model: 'insurance.information',
                views: [[false, 'list'], [false, 'form']],
                target: 'current'
            });
        },
         view_total_claim : function (ev){
           ev.preventDefault();
           return this.do_action({
               name: _t('Total Claims'),
               type: 'ir.actions.act_window',
               res_model: 'claim.information',
               views: [[false, 'list'], [false, 'form']],
               target: 'current'
         });
       },
       view_submit_claim : function (ev){
         ev.preventDefault();
         return this.do_action({
             name: _t('Submit Claims'),
             type: 'ir.actions.act_window',
             domain: [['state', '=', 'submit']],
             res_model: 'claim.information',
             views: [[false, 'list'], [false, 'form']],
             target: 'current'
         });
       },
       view_approved_claim : function (ev){
           ev.preventDefault();
           return this.do_action({
               name: _t('Approved Claims'),
               type: 'ir.actions.act_window',
               domain: [['state', '=', 'approved']],
               res_model: 'claim.information',
               views: [[false, 'list'], [false, 'form']],
               target: 'current'
           });
       },
       view_not_approved_claim : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Not Approved Claims'),
                type: 'ir.actions.act_window',
                domain: [['state', '=', 'not_approved']],
                res_model: 'claim.information',
                views: [[false, 'list'], [false, 'form']],
                target: 'current'
            });
        },
        view_res_partner_agent : function (ev){
            ev.preventDefault();
            return this.do_action({
                name: _t('Agents'),
                type: 'ir.actions.act_window',
                domain: [['is_agent', '=', 'True']],
                res_model: 'res.partner',
                views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
                target: 'current'
            });
        },

        get_action: function (ev, name, res_model){
            ev.preventDefault();
            return this.do_action({
                name: _t(name),
                type: 'ir.actions.act_window',
                res_model: res_model,
                views: [[false, 'kanban'],[false, 'tree'],[false, 'form']],
                target: 'current'
            });
        },


       apexGraph: function () {
            Apex.grid = {
                padding: {
                    right: 0,
                    left: 0,
                    top: 10,
                }
            }
            Apex.dataLabels = {
                enabled: false
            }
        },

       claimApprovedNotApproved: function(data){
        const options = {
          series: [
            {
            name: 'Claim',
            data: data[1]
            }
          ],
        chart: {
          height: 400,
          type: 'bar',
          events: {
            click: function(chart, w, e) {
              // console.log(chart, w, e)
            }
          }
        },
        colors: ['#460C68', '#CB1C8D', '#395144'],
        plotOptions: {
          bar: {
            columnWidth: '10%',
            distributed: true,
          }
        },
        dataLabels: {
          enabled: false
        },
        legend: {
          show: false
        },
        xaxis: {
            categories: data[0],
            labels: {
                style: {
                    colors: ['#460C68', '#CB1C8D', '#395144'],
                    fontSize: '12px'}
            }
        }
        };
        this.renderGraph("#claim_approve_not_approve", options);
        },

    insuranceStateCondition: function(data){
        const options = {
            series: [{ name: 'Insurance', data: data[1]}],
            chart: {
            height: 400,
            type: 'bar',
            events: {
                click: function(chart, w, e) {
                // console.log(chart, w, e)
                }
            }
            },
        colors: ['#FF6464', '#000000'],
        plotOptions: {
            bar: {
                columnWidth: '10%',
                distributed: true,
            }
        },
        dataLabels: {
            enabled: false
        },
        legend: {
            show: false
        },
        xaxis: {
            categories: data[0],
            labels: {
                style: {
                colors: ['#FF6464', '#000000'],
                fontSize: '12px'}
            }
        }
        };
    this.renderGraph("#insurance_state", options);
    },

       insuranceTopAgent: function(data){
        const options = {
                series: data[1],
                chart: {
                    type: 'donut',
                    height: 410
                },
                colors: ['#ADA2FF', '#E0144C', '#D6E4E5', '#F49D1A'],
                dataLabels: {
                    enabled: false
                },
                labels: data[0],
                legend: {
                    position: 'bottom',
                },
            };
       this.renderGraph("#insurance_top_agent", options);
       },

       genderCount: function(data){
       const options = {
          series: data[1],
          chart: {
          width: 500,
          height: 500,
          type: 'pie',
        },
        labels:  data[0],
        responsive: [{
          breakpoint: 480,
          options: {
            chart: {
              width: 200
            },
            legend: {
              position: 'bottom'
            }
          }
        }]
        };
       this.renderGraph("#customer_gender", options);
       },

          renderGraph: function(render_id, options){
            $(render_id).empty();
            const graphData = new ApexCharts(document.querySelector(render_id), options);
            graphData.render();
        },

        willStart: function () {
            const self = this;
            return this._super()
            .then(function() {});
        },
    });
    core.action_registry.add('insurance_dashboard', ActionMenu);
});
