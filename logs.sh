#!/bin/bash
docker-compose -f /opt/multi_agent_travel/docker-compose.prod.yml logs -f --tail=100
