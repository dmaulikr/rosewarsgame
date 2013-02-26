package com.wotr.strategy.action;

import java.util.Collection;
import java.util.Map;

import com.wotr.model.Direction;
import com.wotr.model.Position;
import com.wotr.model.unit.Unit;

public interface ActionResolverStrategy {

	boolean isMoveable(Unit unit, Position pos, Direction direction, Map<Position, Unit> attackingUnits, Map<Position, Unit> defendingUnits, int pathProgress);

	boolean isAttackable(Unit unit, Position pos, Direction direction, Map<Position, Unit> attackingUnits, Map<Position, Unit> defendingUnits, int pathProgress);	

	int getPathLength(Unit unit, Position pos, Direction direction, Map<Position, Unit> attackingUnits, Map<Position, Unit> defendingUnits, int pathProgress);

	Collection<Direction> getDirections(Unit unit, Position pos, Direction direction, Map<Position, Unit> attackingUnits, Map<Position, Unit> defendingUnits, int pathProgress);

}