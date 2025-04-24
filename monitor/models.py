from django.db import models
import socket

class OpenPort(models.Model):
    port = models.IntegerField()
    pid = models.IntegerField()
    process_name = models.CharField(max_length=255)

    def __str__(self):
        return f"Port {self.port} ({self.process_name})"

class CPUUsage(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_usage = models.FloatField()

    def __str__(self):
        return f"CPU Usage at {self.timestamp}: {self.cpu_usage}%"

class EstablishedConnection(models.Model):
    ip = models.GenericIPAddressField()
    hostname = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Connection from {self.ip} ({self.hostname or 'Inconnu'})"

class BandwidthUsage(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    sent_kb = models.FloatField()
    received_kb = models.FloatField()
    total_kb = models.FloatField()

    def __str__(self):
        return f"Bandwidth Usage at {self.timestamp}: Sent {self.sent_kb} KB, Received {self.received_kb} KB"

class CronJobModification(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=255)
    details = models.TextField()

    def __str__(self):
        return f"Cron Job Modification at {self.timestamp}: {self.message}"

class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return f"Log at {self.timestamp}: {self.message}"

class OutboundTraffic(models.Model):
    local_address = models.CharField(max_length=255)
    remote_address = models.CharField(max_length=255)
    remote_port = models.IntegerField()
    process = models.CharField(max_length=255, null=True, blank=True)
    packets_sent = models.BigIntegerField()
    packets_received = models.BigIntegerField()

    def __str__(self):
        return f"Outbound traffic from {self.local_address} to {self.remote_address}:{self.remote_port}"

