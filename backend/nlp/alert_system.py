# backend/nlp/alert_system.py
class AlertSystem:
    def check_alerts(self, recent_reviews):
        alerts = []
        
        # Sudden spike in negative reviews
        if self.detect_negative_spike(recent_reviews):
            alerts.append({
                'type': 'critical',
                'message': 'Negative review spike detected',
                'action': 'Investigate product quality immediately'
            })
        
        # Competitor mentions increasing
        if self.detect_competitor_trend(recent_reviews):
            alerts.append({
                'type': 'warning',
                'message': 'Increased competitor comparisons',
                'action': 'Review competitive positioning'
            })
        
        return alerts