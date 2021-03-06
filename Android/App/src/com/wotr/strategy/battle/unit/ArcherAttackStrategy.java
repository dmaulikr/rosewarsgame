package com.wotr.strategy.battle.unit;

import com.wotr.model.UnitType;
import com.wotr.model.unit.Unit;
import com.wotr.strategy.battle.DefaultAttackStrategy;

public class ArcherAttackStrategy extends DefaultAttackStrategy {

	@Override
	protected boolean performAttack(int attackRoll, Unit attackingUnit, Unit defendingUnit) {

		// if defending is of type infantry
		if (defendingUnit.getType().equals(UnitType.INFANTRY)) {
			return attackRoll >= attackingUnit.getAttackAttribute().calculateValue() - 1;
		}
		return super.performAttack(attackRoll, attackingUnit, defendingUnit);
	}
}
