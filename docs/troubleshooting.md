# Troubleshooting Guide

## Common Issues

### 1. Logs Not Appearing in Dashboard

**Symptoms:** No events showing up despite logs being generated

**Checks:**
1. Verify log collection:
```bash
docker-compose logs filebeat
```

2. Check Redis queue:
```bash
redis-cli
> LLEN events:raw
```

3. Check detection engine processing:
```bash
docker-compose logs detection-engine | grep "Events processed"
```

**Solution:**
- Ensure log paths are correct in `config/filebeat/filebeat.yml`
- Verify Redis is reachable
- Check detection engine is running

### 2. Alerts Not Firing

**Symptoms:** No alerts despite matching events

**Checks:**
1. Verify rule syntax:
```bash
python scripts/testing/test_detection_rules.py
```

2. Check rule loading:
```bash
docker-compose logs detection-engine | grep "Rules loaded"
```

3. Test rule manually:
```bash
# Generate test event
python scripts/testing/generate_test_logs.py
```

**Solution:**
- Fix YAML syntax errors in rules
- Ensure rules are enabled
- Check timeframe and threshold values

### 3. High Memory Usage

**Symptoms:** System running out of memory

**Checks:**
```bash
docker stats
```

**Solutions:**
- Reduce OpenSearch heap size in `docker-compose.yml`
- Decrease batch sizes in detection engine
- Scale down worker counts
- Increase host RAM

### 4. Performance Issues

**Symptoms:** Slow dashboard, delayed processing

**Checks:**
1. Check queue depth:
```bash
redis-cli LLEN events:raw
```

2. Check OpenSearch health:
```bash
curl http://localhost:9200/_cluster/health
```

**Solutions:**
- Scale detection workers:
```bash
docker-compose up -d --scale detection-engine=4
```

- Add OpenSearch nodes
- Optimize detection rules
- Increase batch sizes

### 5. Connection Errors

**Symptoms:** Services can't connect to each other

**Checks:**
```bash
docker network ls
docker network inspect lightweight-siem_siem-network
```

**Solution:**
- Restart services
- Check Docker network
- Verify environment variables

### 6. Email Notifications Not Working

**Checks:**
1. Verify SMTP settings in `.env`
2. Check alert manager logs:
```bash
docker-compose logs alert-manager | grep email
```

**Solutions:**
- Test SMTP credentials
- Enable "Less secure apps" for Gmail
- Use app-specific password
- Check firewall rules

## Getting Help

If issues persist:

1. Check logs:
```bash
docker-compose logs --tail=100 <service-name>
```

2. Enable debug mode:
```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG
```

3. GitHub Issues: Report at repository issues page

4. Community: Join discussions forum
